FROM bitnami/minideb:buster

WORKDIR /opt/demo_content_aggregator

COPY . .

RUN apt-get update  -y && \
    apt-get install -y \
    python3-dev \
    swig \
    cython3  \
    python3-pip && \
python3 setup.py install && \
apt-get remove -y python3-dev && \
apt-get autoremove -y && \
apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH "${PYTHONPATH}:./"

CMD /usr/bin/python3 ./content_aggregator/content_aggregator.py -p ./.env.yaml