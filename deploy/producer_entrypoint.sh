#!/bin/bash

cd /cloud_trading/producer
uvicorn kafka_producer:app