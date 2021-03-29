#!/usr/bin/env python3
# coding=utf-8
"""
The main executable module
"""
import argparse

from aiohttp import web
from aiohttp.web import middleware
from aiohttp.web import HTTPException

from mypackages import peewee_models
from mypackages import settings_loader
from mypackages import logging_repository


class ServerAggregator:
    """
    Main class
    """
    def __init__(self, config: dict[str, [str, int]]):
        self.log = None
        self._config = config
        self.logging_repository_ = logging_repository.LoggingRepository(dict(tag='DemoAggregatorServer',
                                                                             worker='ServerAggregator'),
                                                                        ping_host=self._config['logging_logstash_host'],
                                                                        ping_port=self._config['logging_logstash_port'],
                                                                        config=config)
        self.log = self.logging_repository_.log  # init log obj
        # ORM peewee-async
        self._database = peewee_models.PeeweeRepositoryBuilder()(peewee_models, config)  # init db connect
        self.dao = peewee_models.Manager(self._database)  # init data access object

        self._app = web.Application(middlewares=[self.middleware])
        self._app.on_startup.append(self._initialize)
        self._app.on_shutdown.append(self._terminate)

        self._app.add_routes([
            web.get('/pages', self._pages_handler, name='pages'),  # list pages
            # list block on page
            web.get('/page/{page_slug}', self._page_handler, name='page'),
        ])

    async def _page_handler(self, request):
        page_slug = request.match_info.get('page_slug', None)
        self.log.debug(f'request page with slug: {page_slug}')
        if not page_slug:
            raise web.HTTPBadRequest()

        try:
            page_obj = await self.dao.get(peewee_models.Pages, slug=page_slug)
            # join table relation & block but return only block
            blocks_obj = await (
                self.dao.execute(peewee_models.Blocks.select(
                ).join(
                    peewee_models.PagesBlocksRelationship,
                    on=(peewee_models.Blocks.id == peewee_models.PagesBlocksRelationship.block_id)
                ).where(
                    peewee_models.PagesBlocksRelationship.page_id == page_obj.id
                ).order_by(
                    peewee_models.PagesBlocksRelationship.order_by)))

        except peewee_models.DoesNotExist as e:
            self.log.debug(f'{e}')
            raise web.HTTPFound('/redirect')
        except peewee_models.PeeweeException as e:
            self.log.error(f"connection DB error: {e}")
            raise

        # update all blocks at once
        if not bool(await peewee_models.Blocks.multiple_obj_inc_viewed(blocks_obj)):
            self.log.error(f'for page {page_obj} the blocks viewing update is failed')

        # You can specify which fields to output with the only parameter: b.model_to_dict(only=['id'])
        blocks_serialize = [await b.model_to_dict() for b in blocks_obj]
        return web.json_response(blocks_serialize)

    async def _pages_handler(self, request):
        self.log.debug('request pages list')
        try:
            pages_obj = await (self.dao.execute(peewee_models.Pages.select(
            ).order_by(
                peewee_models.Pages.order_by)))

        except (peewee_models.DoesNotExist, peewee_models.PeeweeException) as e:
            self.log.error(f"connection DB error: {e}")
            raise

        pages_serialize = [
            {'name': p.name, 'link': str(request.url.join(request.app.router['page'].url_for(page_slug=p.slug)))}
            for p in pages_obj]

        return web.json_response(pages_serialize)

    @middleware
    async def middleware(self, request, handler):
        try:
            resp = await handler(request)
            return resp
        except HTTPException as e:
            return web.json_response({e.status_code: e.reason})

    async def _initialize(self, app):
        self.log.info('Server is starting')

    async def _terminate(self, app):
        self.log.info('Server is downing')

    def listen(self):
        """
        start application
        """
        web.run_app(self._app,
                    host=self._config['application_listen_host'],
                    port=self._config['application_listen_port'])


def main(path_to_config: str):
    manager_server = ServerAggregator(settings_loader.load_config(path_to_config=path_to_config))
    manager_server.listen()


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-p", action='store', type=str, dest='PATHTOCONFIG',
                            help="Specify the path to the config  file")
    args = arg_parser.parse_args()
    main(args.PATHTOCONFIG)
