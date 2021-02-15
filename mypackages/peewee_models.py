#!/usr/bin/env python3
# coding=utf-8
"""
Models for ORM peewee-async
"""
import argparse
from datetime import datetime
from typing import Any, Callable

import peewee
import peewee_asyncext
from peewee_async import Manager
from peewee import PeeweeException, DoesNotExist, ModelSelect, CharField
from playhouse.postgres_ext import JSONField
from marshmallow_peewee import ModelSchema
from marshmallow import Schema, fields
from playhouse.shortcuts import model_to_dict

from mypackages import settings_loader

__all__ = ['PeeweeException', 'BaseRepositoryPeeweeException', 'PeeweeRepositoryBuilder', 'Manager', 'Pages', 'Blocks']

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
    name = peewee.CharField(null=True, db_column='name', help_text='page name')
    slug = peewee.CharField(null=True, db_column='slug', help_text='slug for url')
    order_by = peewee.SmallIntegerField(null=True, db_column='order_by', help_text='order for viewing')


class Blocks(BaseModel):
    name = peewee.CharField(null=True, db_column='name', help_text='block name')
    links = JSONField(null=True, db_column='links', help_text='it is links video staff for block')
    viewed_count = peewee.IntegerField(null=True, db_column='viewed_count', help_text='contain viewed count')


class PagesBlocksRelationship(BaseModel):
    """
    There is a many-to-many relationship for pages & block
    """
    page_id = peewee.ForeignKeyField(Pages, db_column='page_id', help_text='foreign key to table "pages"')
    block_id = peewee.ForeignKeyField(Blocks, db_column='block_id', help_text='foreign key to table "block"')
    order_by = peewee.SmallIntegerField(null=True, db_column='blocks_order_by', help_text='blocks order for viewing')

    class Meta:
        database = DATABASE  # closure
        # TODO unique together page & block
        indexes = (
            (('page_id', 'block_id'), True),  # Note the trailing comma!
        )


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


def migration():
    # page = Pages(name='main_page', slug='main_page_slug', order_by=10)
    page = Pages().create(name='main_page', slug='main_page_slug', order_by=10)
    block_1 = Blocks().create(name='first_block', links='https://www.youtube.com/', order_by=10, viewed_count=0)
    block_2 = Blocks().create(name='second_block', links='https://www.youtube.com/', order_by=20, viewed_count=0)
    relationship = [PagesBlocksRelationship().create(page_id=1, block_id=block_1.id, order_by=20),
                    PagesBlocksRelationship().create(page_id=1, block_id=block_2.id, order_by=10)]
    # page.save()
    # block_1.save()
    # block_2.save()
    # relationship[0].save()
    # relationship[1].save()

    r = PagesSchema().dump(page)
    pass


def main(path):
    """
    Init migration
    """
    config = settings_loader.load_config(prefix=ENV_PREFIX, path_to_config=path)
    database = get_postgresql_database(config)
    DATABASE.initialize(database)
    DATABASE.connect()
    DATABASE.create_tables([Pages, Blocks, PagesBlocksRelationship])
    migration()
    DATABASE.close()


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-p", action='store', type=str, dest='PATHTOCONFIG',
                            help="Specify the path to the config  file")
    args = arg_parser.parse_args()
    main(args.PATHTOCONFIG)
