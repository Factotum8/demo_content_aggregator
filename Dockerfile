FROM python:3.9.2

WORKDIR /opt/demo_content_aggregator

COPY . .

RUN python3 setup.py install

ENV PYTHONPATH "${PYTHONPATH}:./"

CMD /usr/bin/python ./content_aggregator/content_aggregator.py -p ./.env.yaml
