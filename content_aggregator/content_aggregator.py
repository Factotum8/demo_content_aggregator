#!/usr/bin/env python3
# coding=utf-8
"""
The main executable module
"""
import argparse
from typing import Dict, Union

from aiohttp import web

from mypackages import peewee_models
from mypackages import settings_loader
from mypackages import logging_repository


class ServerAggregator:
    """
    Main class
    """
    def __init__(self, config: Dict[str, Union[str, int]]):
        self.log = None
        self._config = config
        self.logging_repository_ = logging_repository.LoggingRepository(dict(tag='DemoAggregatorServer',
                                                                             worker='ServerAggregator'),
                                                                        ping_host=self._config['logging_logstash_host'],
                                                                        ping_port=self._config['logging_logstash_port'],
                                                                        config=config)
        self.log = self.logging_repository_.log  # init log obj
        # ORM peewee-async
        # self._database = peewee_models.PeeweeRepositoryBuilder()(peewee_models, config)  # init db connect
        # self.dao = peewee_models.Manager(self._database)  # init data access object

        self._app = web.Application()
        self._app.on_startup.append(self._initialize)
        self._app.on_shutdown.append(self._terminate)

        # TODO
        self._app.add_routes([
            web.get('/pages', self._pages_handler),  # list pages
            web.get('/page/{page_id}', self._page_handler),  # list block on page
        ])

    async def _page_handler(self, request):
        page_id = request.match_info.get('page_id', 1)
        return web.Response(text=f'page id {page_id}')

    async def _pages_handler(self, request):
        return web.Response(text="hello")

    async def _initialize(self, app):
        pass

    async def _terminate(self, app):
        pass

    def listen(self):
        """
        start application
        """
        web.run_app(self._app,
                    host=self._config['application_listen_host'],
                    port=self._config['application_listen_port'])


def main(path_to_config: str):
    manager_server = ServerAggregator(settings_loader.load_config(prefix=peewee_models.ENV_PREFIX,
                                                                  path_to_config=path_to_config))
    manager_server.listen()


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-p", action='store', type=str, dest='PATHTOCONFIG',
                            help="Specify the path to the config  file")
    args = arg_parser.parse_args()
    main(args.PATHTOCONFIG)
