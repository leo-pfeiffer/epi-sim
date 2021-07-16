![Build status](https://github.com/leo-pfeiffer/msc-thesis/actions/workflows/python-app.yml/badge.svg)
![Online status](https://img.shields.io/website?down_color=lightgrey&down_message=offline&up_color=blue&up_message=online&url=http%3A%2F%2F209.182.235.76%2F)
![codecov](https://codecov.io/gh/leo-pfeiffer/epi-sim/branch/main/graph/badge.svg?token=AK3O2NL82O)

# EpiSim
Repository for my MSc Thesis `A compartmented network model for COVID-19'

### Requirements
This project was developed using Python 3.9 and we recommend using this version. 
However, backward compatibility is given for Python versions 3.6+.

Since the web application and the model can 
be run on its own, the requirements are listed in two separate requirements.txt files:

- `requirements.txt`: Requirements required for modelling
- `app/requirements.txt`: Requirements required for web application

If you want to install all requirements (both app and model) in one go, run

```shell
make requirements
```

from within your virtual environment.

To build the project using docker compose, you also need those installed on your machine
([Docker](https://docs.docker.com/engine/install/), [Docker compose](https://docs.docker.com/compose/install/)).

## Model

### Setup
For the setup of the modelling environment, create a virtual enviromnet in the 
project directory, activate it and call `make setup`.

```shell
python -m venv venv
source venv/bin/acitvate

make setup
```

This will install all requirements in your virtual environmant and generates
the required .env files.

### Analysis

todo....

## Web Application `EpiSim`
The web application can be run independently of the model. You can either 
build it using docker compose (recommended for production) or the built-in
Flask server (recommended for development).

The application is deployed under the following URL:
todo

### Build web app with docker compose
The web application can be built using docker compose using Nginx as the HTTP server 
and uWSGI as the application server.

To build the application, run

```shell
make build
```

This also generates the required env files (if they don't exist yet).

Go to http://localhost:4401.

### Run web app without build
Alternatively, you can also run the web app using the builtin server, which is not suitable for 
production but much simpler for development and test purposes.

```shell
make run
```

This also generates the required env files (if they don't exist yet).

Go to http://localhost:4401

### Data source of the application
For easy access and updating of the simulation data underlying the application,
the data is stored in a [public data git repository hosted on GitHub](https://github.com/leo-pfeiffer/msc-thesis-data).

todo
However, the data source can be changed to any URL via the .env variable ....