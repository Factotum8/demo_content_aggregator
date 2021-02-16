# demo_content_aggregator
It is test task by applying for job.  
## Description  
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
   
## Install requirements
1. Follow to project directory (Directory contains README.md file).
2. Create or activate environment python by any way.
3. Production requirements: `python setup.py install`.
4. Test requirements: `pip install -e .[test]` (if necessary).
   
## Run
1. Follow to project directory (Directory contains README.md file).
2. Execute: `sudo docker-compose up` 

## Sources
* /content_aggregator/content_aggregator.py - main module  
  Project submodules:
* /mypackages/logging_repository.py
* /mypackages/peewee_models.py
* /mypackages/settings_loader.py

### Configure files
* .db_env.yaml - config for db  
* .env.yaml - config for application

## Migration
1. Follow to project directory (Directory contains README.md file).
2. Create or activate environment python by any way.
3. Execute: `python ./fixture.py -p ./.env.yaml`

## Fixture
1. Follow to project directory (Directory contains README.md file).
2. Create or activate environment python by any way.
3. Execute: `python ./fixture.py -p ./.env.yaml -f`

## RUN TEST 
    pass

## License
[LICENSE MIT](LICENSE)