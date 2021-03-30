FROM python:3.9

WORKDIR /opt/demo_content_aggregator

COPY . .

RUN python setup.py install

ENV PYTHONPATH "${PYTHONPATH}:./"

CMD python ./content_aggregator/content_aggregator.py -p ./.env.yaml
