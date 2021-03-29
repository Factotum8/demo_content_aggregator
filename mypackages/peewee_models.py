#!/usr/bin/env python3
# coding=utf-8
r"""
Example
=======

The module is models for ORM peewee-async.
There are 3 tables:

+----------------------+-------------------------+---------------+
| Pages                | PagesBlocksRelationship | Blocks        |
+======================+=========================+===============+
| ``name``             | page_id                 | name          |
+----------------------+-------------------------+---------------+
| ``slug``             | block_id                | links         |
+----------------------+-------------------------+---------------+
| ``order_by``         | order_by                | viewed_count  |
+----------------------+-------------------------+---------------+

**'Pages' & 'Blocks' were connected by 'PagesBlocksRelationship'.
The classes: BaseSchema, PagesSchema, BlocksSchema, RelationshipSchema just are serializers.**
"""
from typing import Union

import peewee
import peewee_asyncext
from peewee_async import Manager
from peewee import PeeweeException, DoesNotExist
from playhouse.postgres_ext import JSONField
from marshmallow_peewee import ModelSchema

__all__ = ['PeeweeException', 'BaseRepositoryPeeweeException', 'PeeweeRepositoryBuilder', 'Manager', 'Pages', 'Blocks',
           'DoesNotExist', 'DATABASE', 'get_postgresql_database', 'PagesBlocksRelationship']

# This instruction is the correct way to dynamically defining a database
DATABASE = peewee.DatabaseProxy()


class BaseRepositoryPeeweeException(Exception):
    """
    Base exception for this repository
    """
    pass


class BaseModel(peewee.Model):
    """
    model definitions - the standard "pattern" is to define a base model class
    that specifies which database to use.  then, any subclasses will automatically
    use the correct storage.
    """

    class Meta:
        database = DATABASE  # closure


def get_postgresql_database(config: dict) -> peewee_asyncext.PostgresqlExtDatabase:
    """
    Init db obj and return
    """
    return peewee_asyncext.PostgresqlExtDatabase(
        config['pg_db_name'],
        user=config['pg_db_login'],
        password=config['pg_db_pass'],
        host=config['pg_db_host'],
        port=config['pg_db_port'],
    )


def init_postgresql_database(config: dict):
    DATABASE.initialize(get_postgresql_database(config))
    DATABASE.connect()
    return DATABASE


class Pages(BaseModel):
    """
    Model for table pages
    """
    name = peewee.CharField(null=True, db_column='name', help_text='page name')
    slug = peewee.CharField(null=True, db_column='slug', help_text='slug for url', index=True, unique=True)
    order_by = peewee.SmallIntegerField(null=True, db_column='order_by', help_text='order for viewing', index=True)

    async def model_to_json(self, **kwargs) -> str:
        return PagesSerializerSchema(**kwargs).dumps(self)

    async def model_to_dict(self, **kwargs) -> dict:
        return PagesSerializerSchema(**kwargs).dump(self)


class Blocks(BaseModel):
    """
    Model for table blocks
    """
    name = peewee.CharField(null=True, db_column='name', help_text='block name')
    links = JSONField(null=True, db_column='links', help_text='it is links video staff for block')
    viewed_count = peewee.IntegerField(null=True, db_column='viewed_count', help_text='contain viewed count')

    async def model_to_json(self, **kwargs) -> str:
        return BlocksSerializerSchema(**kwargs).dumps(self)

    async def model_to_dict(self, **kwargs) -> dict:
        return BlocksSerializerSchema(**kwargs).dump(self)

    async def model_to_dict_and_inc_viewed(self, **kwargs) -> dict:
        """
        Convert model's object to dict and INCREMENT counter from db
        """
        self.viewed_count += 1
        self.save()
        return await self.model_to_dict(**kwargs)

    @classmethod
    # async def multiple_obj_inc_viewed(cls, objects: tuple['Blocks']) -> Union[None, int]:
    async def multiple_obj_inc_viewed(cls, objects: tuple['Blocks']) -> Union[None, int]:
        # see https://peewee.readthedocs.io/en/latest/peewee/query_operators.html
        query = Blocks.update(viewed_count=Blocks.viewed_count+1).where(Blocks.sell_currency << [b.id for b in objects])
        return query.execute()


class PagesBlocksRelationship(BaseModel):
    """
    There is a many-to-many relationship for pages & block
    """
    page_id = peewee.ForeignKeyField(Pages, db_column='page_id', help_text='foreign key to table "pages"')
    block_id = peewee.ForeignKeyField(Blocks, db_column='block_id', help_text='foreign key to table "block"')
    order_by = peewee.SmallIntegerField(null=True, db_column='blocks_order_by', help_text='blocks order for viewing')

    class Meta:
        database = DATABASE  # closure
        # unique together page & block
        indexes = (
            # a unique if True
            (('page_id', 'block_id'), True),  # Note the trailing comma!
        )

    async def model_to_json(self, **kwargs) -> str:
        return RelationshipSerializerSchema(**kwargs).dumps(self)


class PeeweeRepositoryBuilder:
    """
    Create data access object
    """

    def __init__(self):
        self.module = None

    def __call__(self, module, config: dict):
        return self.create_repository(module, config)

    def __del__(self):
        try:
            self.module.close()
        except Exception:
            pass

    def create_repository(self, module, config: dict):
        """
        Create peewee connector
        :param module: peewee_models
        :param config:
        :return:
        """
        module.DATABASE.initialize(self.connect(module, config))
        module.DATABASE.connect()
        self.module = module
        return module.DATABASE

    @staticmethod
    def connect(module, config: dict) -> peewee.PostgresqlDatabase:
        return module.get_postgresql_database(config)


class BaseSerializerSchema(ModelSchema):
    """
    Base marshmallow schema for serializer
    """


class PagesSerializerSchema(BaseSerializerSchema):
    """
    serializer from ORM obj to json obj
    """
    class Meta:
        model = Pages


class BlocksSerializerSchema(BaseSerializerSchema):
    """
    serializer from ORM obj to json obj
    """
    class Meta:
        model = Blocks


class RelationshipSerializerSchema(BaseSerializerSchema):
    """
    serializer from ORM obj to json obj
    """
    class Meta:
        model = PagesBlocksRelationship


if __name__ == '__main__':
    pass
