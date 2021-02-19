#!/usr/bin/env python3
# coding=utf-8
"""
Models for ORM peewee-async
"""
import peewee
import peewee_asyncext
from peewee_async import Manager
from peewee import PeeweeException, DoesNotExist
from playhouse.postgres_ext import JSONField
from marshmallow_peewee import ModelSchema

__all__ = ['PeeweeException', 'BaseRepositoryPeeweeException', 'PeeweeRepositoryBuilder', 'Manager', 'Pages', 'Blocks',
           'DoesNotExist', 'DATABASE', 'get_postgresql_database', 'PagesBlocksRelationship', 'ENV_PREFIX']

ENV_PREFIX = 'AGGREGATOR_'  # We delete this prefix from environment variables
# This instruction is the correct way to dynamically defining a database
DATABASE = peewee.DatabaseProxy()


class BaseRepositoryPeeweeException(Exception):
    """
    Base exception for this repository
    """
    pass


class BaseModel(peewee.Model):
    """
    model definitions -- the standard "pattern" is to define a base model class
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
        return PagesSchema(**kwargs).dumps(self)

    async def model_to_dict(self, **kwargs) -> dict:
        return PagesSchema(**kwargs).dump(self)


class Blocks(BaseModel):
    """
    Model for table blocks
    """
    name = peewee.CharField(null=True, db_column='name', help_text='block name')
    links = JSONField(null=True, db_column='links', help_text='it is links video staff for block')
    viewed_count = peewee.IntegerField(null=True, db_column='viewed_count', help_text='contain viewed count')

    async def model_to_json(self, **kwargs) -> str:
        return BlocksSchema(**kwargs).dumps(self)

    async def model_to_dict(self, **kwargs) -> dict:
        return BlocksSchema(**kwargs).dump(self)

    async def model_to_dict_and_inc_viewed(self, **kwargs) -> dict:
        """
        Convert model's object to dict and INCREMENT counter from db
        """
        self.viewed_count += 1
        self.save()
        return await self.model_to_dict(**kwargs)


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
        return RelationshipSchema(**kwargs).dumps(self)


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


class BaseSchema(ModelSchema):
    """
    Base marshmallow schema
    """


class PagesSchema(BaseSchema):
    class Meta:
        model = Pages


class BlocksSchema(BaseSchema):
    class Meta:
        model = Blocks


class RelationshipSchema(BaseSchema):
    class Meta:
        model = PagesBlocksRelationship


if __name__ == '__main__':
    pass
