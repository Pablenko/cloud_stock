FROM python:3.8.12-buster AS consumer

COPY requirements.txt /
RUN pip install --upgrade pip && pip install --no-cache-dir -r /requirements.txt

COPY . /cloud_trading
WORKDIR /cloud_trading
RUN python setup.py install

ENTRYPOINT ["/bin/sh", "/cloud_trading/deploy/engine_entrypoint.sh"]

FROM python:3.8.12-buster AS producer

COPY requirements.txt /
RUN pip install --upgrade pip && pip install --no-cache-dir -r /requirements.txt

COPY . /cloud_trading
WORKDIR /cloud_trading
RUN python setup.py install

ENTRYPOINT ["/bin/sh", "/cloud_trading/deploy/producer_entrypoint.sh"]

FROM python:3.8.12-buster AS service_discovery

COPY requirements.txt /
RUN pip install --upgrade pip && pip install --no-cache-dir -r /requirements.txt

COPY . /cloud_trading
WORKDIR /cloud_trading
RUN python setup.py install

ENTRYPOINT ["/bin/sh", "/cloud_trading/deploy/service_discovery_entrypoint.sh"]