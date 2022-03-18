#!/bin/bash

docker build -t cloud_trading_consumer:latest --target consumer .
docker build -t cloud_trading_producer:latest --target producer .
docker build -t cloud_trading_discovery:latest --target service_discovery .