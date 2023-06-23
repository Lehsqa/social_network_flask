## Intro

This repo is intended to make it easy to get started with a Flask project. If you want to use it for your own projects, I suggest cloning this repo locally rather than following the installation instructions below:

```
git clone https://github.com/Lehsqa/social_network_flask.git <project-name>
```

## Installation (Docker)

Create a new docker container, using docker-compose file and generate structures for DB:

```sh
docker-compose up -d --build

docker-compose exec social_network_app python project/manage.py create_db
```

## Installation (Python)

Generate structures for DB, using manage.py:

```sh
python project/manage.py create_db
```

## Running

Docker:

```sh
docker-compose up
```

Python on local host (inside the root of project):

```sh
flask --app project/app run
```