# demo_content_aggregator
It is test task by applying for job.  
## The task description
*I have received it on russian language.*  
Технологии:
- aiohttp 
- postgresql 
- async peewee 
- marshmallow  
  
Нужно сделать бэкэнд-api, который хранит в базе страницы с контентом. 
У страницы есть название, слаг, порядок сортировки и несколько (любое количество) контент-блоков. У блока есть название, ссылка на видео-файл, сортировки на странице, количество показов. 
Один и тот же контент-блок может быть на разных страницах. 
Нужно реализовать 2 эндпоинта, которые выводят. 

1. Список страниц. На списке страниц выводятся название блока и ссылка на страницу. Блоки не выводятся, выводится только название и ссылка на страницу.
2. Страница с блоками. На странице выводятся блоки и счетчики показа блоков. 
Добавление, изменение, удаление делать не нужно. Нужно сделать фикстуру, которая заполнит таблицы в базе, чтобы можно было развернуть проект и продемонстрировать его работу.	
Для каждого контент блока нужно подсчитывать, сколько раз он показывался пользователю.
   
## Example
Request:  
`
curl -s localhost:8072/pages | jq
`  
Reply:  
`
[
  {
    "name": "main_page",
    "link": "http://localhost:8072/page/main_page_slug"
  },
  {
    "name": "second_page",
    "link": "http://localhost:8072/page/second_page_slug"
  }
]
`

## Run
With Docker:  
1. Follow to project directory (Directory contains README.md file).
2. Execute: `sudo docker-compose up`  

 Without Docker:
1. Run DB instance.
2. Install [requirements](#install-requirements)
3. Specify `.env.yaml` or environment variable.
4. Follow to project directory (Directory contains README.md file).
5. Exec `python ./content_aggregator/content_aggregator.py -p .env.yaml`

## Install requirements
**It doesn't necessary if you use Docker & docker-compose.**
1. Follow to project directory (Directory contains README.md file).
2. Create or activate environment python by any way.
3. Production requirements: `python setup.py install`.
4. Test requirements: `pip install -e .[test]` (if necessary).

## Sources
* /content_aggregator/content_aggregator.py - main module with a business logic.  
  Project submodules:
* /mypackages/logging_repository.py - logging to console, file, logstash.
* /mypackages/peewee_models.py - the data model for peewee ORM.
* /mypackages/settings_loader.py - configure from setting file and env variables.  

### Configure files
* .db_env.yaml - config for db  
* .env.yaml - config for application

## Migration
1. Follow to project directory (Directory contains README.md file).
2. Create or activate environment python by any way.
3. Execute: `python ./fixture.py -p ./.env.yaml` or 
   if you use docker-compose `docker-compose exec aggregator python ./fixture.py -p ./.env.yaml`

## Fixture
1. Follow to project directory (Directory contains README.md file).
2. Create or activate environment python by any way.
3. Execute: `python ./fixture.py -p ./.env.yaml -f` or
   if you use docker-compose `docker-compose exec aggregator python ./fixture.py -p ./.env.yaml -f`

## RUN TEST 
    pass

## License
[LICENSE MIT](LICENSE)