![Build status](https://github.com/leo-pfeiffer/msc-thesis/actions/workflows/python-app.yml/badge.svg)
![Online status](https://img.shields.io/website?down_message=offline&up_message=online&url=http%3A%2F%2Fepi-sim.live)
![codecov](https://codecov.io/gh/leo-pfeiffer/epi-sim/branch/main/graph/badge.svg?token=AK3O2NL82O)

# EpiSim
Repository for my MSc Thesis `A compartmented network model for COVID-19'

---
+ [:rocket: Quickstart](#quickstart)
+ [:gear: Make](#make)
+ [:card_index_dividers: Project Structure](#project-structure)
+ [:safety_pin: Requirements](#requirements)
+ [:stethoscope: Testing](#testing)
+ [:chart_with_upwards_trend: Lib](#lib)
  - [Setup](#setup)
  - [Analysis](#analysis)
+ [:globe_with_meridians: Web Application](#web-application-episim)
  - [Build with Docker Compose](#build-web-app-with-docker-compose-prod--dev)
  - [Run with Flask](#run-web-app-with-flask-only-dev)
  - [Data sources](#data-source-of-the-application)
---

## Quickstart

Execute the following steps for the basic setup of the project.

```shell
git clone https://github.com/leo-pfeiffer/epi-sim.git
cd epi-sim
python -m venv venv
source venv/bin/activate
make setup
```

For the setup of only the `lib`, see [here](#lib).  
For the setup/build of only the `app`, see [here](#web-application-episim)

## Make
We provide a Makefile with the following commands:

```text
==============================================================
Available Make commands ======================================
==============================================================
For Docker commands: default is ENV=prod; for dev set ENV=dev)
==============================================================
requirements_lib           Install pip requirements for lib only
requirements_app           Install pip requirements for app only
requirements               Install all pip requirements
env                        Generate .env files
setup                      Full setup of the project
setup_lib                  Setup of lib only
setup_app                  Setup of the project
test                       Run all unit tests
test_app                   Run unit tests for app
test_lib                   Run unit tests for lib
create_app_data            Create data for web app from simulation results
batch_upload_experiments   Upload experiment results
run                        Run web app with Flask dev server (dev only)
build                      Build web app with docker-compose
up                         Start existing container 
down                       Stop running container 
logs                       Attach docker compose logs 
bash                       Start bash inside container 
destroy                    Shut down containers, remove volumes, remove images
restart                    Restart container 
clear-data                 Clear downloaded app data
help                       Print available commands
```

To see this output, run ```make help```.

## Project Structure

The project contains three top-level folders:

#### `app` (red in the diagram)
Contains the sources for the EpiSim web application.
- `app/app`: Dash web application
- `app/nginx`: NGINX server for production

#### `lib` (blue in the diagram)
Contains the source code for the epidemic models, networks, as well as the 
experiments run with these models.
- `lib/experiments`: Contains Jupyter notebooks and utils for running the simulations, 
  running analyses, and creating output for the thesis
- `lib/model`: Contains epidemic models and networks

#### `setup` (green in the diagram)
Contains setup scripts and .env file templates used in the setup.

![Project Structure][img-project-structure]


## Requirements
We developed the project using Python 3.9, and recommend using this version. 
However, the project is backward compatible for Python versions 3.6+.

Since the `app` and the `lib` can be used independently of each other, 
the requirements are listed in two separate requirements.txt files:

- `lib/requirements.txt`: Requirements required for modelling
- `app/app/requirements.txt`: Requirements required for the web application

If you want to install all requirements (both app and model) in one go, run

```shell
make requirements
```

from within your virtual environment.

To build the project using docker compose, you also need those installed on your machine
([Docker](https://docs.docker.com/engine/install/), [Docker compose](https://docs.docker.com/compose/install/)).

## Testing
Critical features of the project were tested using unit tests.  
You can either run all tests :

```shell
make test
```

... or only those for `lib`:

```shell
make test_lib
```

... or only those for `app`:

```shell
make test_app
```

## Lib

### Setup
For the setup of the modelling environment, create a virtual environment in the 
project directory, activate it and call `make setup`.

```shell
python -m venv venv
source venv/bin/acitvate

make setup
```

This will install all requirements in your virtual environment and generates
the required .env files.

### Data Repo API
The Data Repo API is a simple client for the GitHub API to upload and retrieve
simulation results. The default repo URLs are automatically included in the
.env file when you run `make env`. 

Retrieval is open to anyone (since it's a public repo), however, 
to upload data to a repo, you need to add your own repository URLs.

Both for uploading and downloading files from any repo, you need to add a
GitHub Personal Access token as the DATA_REPO_TOKEN to your .env file.
Learn [here](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token)
how to create such a token.

### Analysis

todo....

## Web Application `EpiSim`
The web application can be run independently of the model. You can either 
build it using docker compose (recommended for production), or the built-in
Flask server (recommended for development).

The application is deployed under the following URL:
todo

### Build web app with docker compose (prod / dev)
The web application can be built using docker compose using Nginx as the HTTP server 
and uWSGI as the application server.

To build the application, run

```shell
make build
```

This also generates the required env files (if they don't exist yet).
By default, this builds the production environment (`ENV=prod`). If you want
to build the dev environment instead, call

```shell
make build ENV=dev
```

The application starts at whichever port is specified in `./app/.env` as an environment
variable for `PORT` (default 80) and `DEV_PORT` (default 4401).

### Run web app with Flask only (dev)
Alternatively, you can also run the web app using the builtin server, which is 
not suitable for production but much simpler for development and test purposes.

```shell
make run
```

This also generates the required env files (if they don't exist yet).
Since this is meant for development only, the `DEV_PORT` specified in `./app/.env`
as an environment variable is used.

### Data source of the application
For easy access and updating of the simulation data underlying the application,
the data is stored in a [public data git repository hosted on GitHub](https://github.com/leo-pfeiffer/epi-sim-data).

todo
However, the data source can be changed to any URL via the .env variable ....


[img-project-structure]: https://github.com/leo-pfeiffer/epi-sim/blob/main/.github/images/project-structure.png
