Ecolex.org
================

[![Docker build](https://dockerbuildbadges.quelltext.eu/status.svg?organization=iucn&repository=ecolex_web)](https://hub.docker.com/r/iucn/ecolex_web/builds)

## Project Name

The Project Name is ECOLEX.

### Requirements

1. one or multiple servers running your choice of Linux flavor (the steps below were tested on CentOS Linux 7).
2. JRE (at least 1.7) on each node.

### Installation

#### Install using Docker
 
In order to install the project for development, you have to clone this repo, gain access to the [ecolex.docker](https://gitlab.com/ecolex/ecolex.docker) gitlab repo and follow the instruction from there.

The project uses 3 docker images ( web, maria and solr) and a docker-compose file located in the gitlab repo.

The images are build and pushed automatically in the following dockerhub repos: [web](https://hub.docker.com/r/iucn/ecolex_web/), [maria](https://hub.docker.com/r/iucn/ecolex_maria/) and [solr](https://hub.docker.com/r/iucn/ecolex_solr/) .

All 3 images are rebuild on every push on the master branch of this repo.
 
 
##### Web image
The image is build using [this](/Dockerfile) Dockerfile. In the [web](/docker/web) directory you can find two sh files(`root-entrypoint.sh` and `entrypoint.sh`) used as entrypoints for docker image, `ecolex.crontab` file containing cron tasks and files used for those tasks (`import_updater.sh`, `reprocess_from_db.sh`) .
 
##### Ecolex Maria image
The image is build from [this](/docker/maria) folder. It contains a [Dockerfile](/docker/maria/Dockerfile) and an entrypoint.
 
##### Ecolex Solr image
The image is build from [this](/docker/solr) folder. It contains a [Dockerfile](/docker/solr/Dockerfile), .sh files and the xml schema which is copied inside the image.

## Django application

We are using Python 3 for the web server application. Initialize an environment with:

    $ pyvenv sandbox
    $ source sanbox/bin/activate
    $ pip install -r requirements.txt

Run with:

    $ ./manage.py runserver

