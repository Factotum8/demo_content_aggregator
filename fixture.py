#!/usr/bin/env python3
# coding=utf-8
"""
Models for ORM peewee-async
"""
import argparse

from mypackages import settings_loader
from mypackages.peewee_models import (DATABASE, get_postgresql_database, Pages, Blocks, PagesBlocksRelationship,
                                      ENV_PREFIX)


def create_fixture():
    """
    Insert into DB and create fixture file
    """
    page = Pages().create(name='main_page', slug='main_page_slug', order_by=10)
    block_1 = Blocks().create(name='first_block', links='https://www.youtube.com/', viewed_count=0)
    block_2 = Blocks().create(name='second_block', links='https://www.youtube.com/', viewed_count=0)
    relationship_1 = PagesBlocksRelationship().create(page_id=page.id, block_id=block_1.id, order_by=20)
    relationship_2 = PagesBlocksRelationship().create(page_id=page.id, block_id=block_2.id, order_by=10)

    page_2 = Pages().create(name='second_page', slug='second_page_slug', order_by=20)
    block_3 = Blocks().create(name='third_block', links='https://www.youtube.com/', viewed_count=0)
    relationship_3 = PagesBlocksRelationship().create(page_id=page_2.id, block_id=block_3.id, order_by=10)

    # Dump fixture to file
    # with open('./fixture_tmp.json', 'w') as f:
    #     json.dump(dict(pages=[PagesSchema().dump(page)],
    #                    blocks=[BlocksSchema().dump(block_1), BlocksSchema().dump(block_2)],
    #                    relationship=[RelationshipSchema().dump(relationship_1),
    #                                  RelationshipSchema().dump(relationship_2)]),
    #               f)


def main(path, with_fixture=False):
    """
    Init migration
    inset test data
    """
    config = settings_loader.load_config(path_to_config=path)
    database = get_postgresql_database(config)
    DATABASE.initialize(database)
    DATABASE.connect()
    DATABASE.create_tables([Pages, Blocks, PagesBlocksRelationship])
    if with_fixture:
        create_fixture()
    DATABASE.close()


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-p', action='store', type=str, dest='PATHTOCONFIG',
                            help='Specify the path to the config file')
    arg_parser.add_argument('-f', action='store_true', dest='ISFIXTURE',
                            help='If up insert test data into DB')
    args = arg_parser.parse_args()
    main(args.PATHTOCONFIG, args.ISFIXTURE)
