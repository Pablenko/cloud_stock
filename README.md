## Cloud stock projecy

Purpose of this project is to create cloud stock platform for trading.
Currently project is in development process. If you have any ideas, feel
free to add issue.

### Technology stack

Kafka, docker-compose, python, FastApi


### Run test environment
```
./build_images.sh
cd deploy && docker-compose up -d
```

### Create orders
```
cd client && python cli.py --ip http://127.0.0.1:8000/
```

### Unit testing
```
pytest -svx
```

### Work in progress

- Switching from docker-compose to Kubernetes
- GUI for order creation/management
- Proper management of engine crash

#### Author
Paweł Przybylski
