[![Build status](https://github.com/leo-pfeiffer/msc-thesis/actions/workflows/python-app.yml/badge.svg)](https://github.com/leo-pfeiffer/msc-thesis/actions/workflows/python-app.yml)

# msc-thesis
Repository for my MSc Thesis `A compartmented network model for COVID-19'

### Requirements
This project was developed using Python 3.9.2. Since the web application and the model can 
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
project directory, activate it and intall the requirements.

```shell
python -m venv venv
source venv/bin/acitvate

pip install -m upgrade pip
pip install -r requirements.txt
```

### Generate mobility network
To generate the mobility network, run:

```shell
make generate-data-paths
```

This generates the required data directories (if they don't exist yet).
To add your own mobility CSV files, put them into the generated 
`data_processing/data/raw` directory. This is optional: if you don't do it, the
notebooks will pull the files from my server.

Then, run the following notebooks in order (all inside `data_processing`):
- `extraction.ipynb`
- `transformation.ipynb`
- `network_creation.ipynb`

To analyse the resulting mobility network, use the `network_analysis.ipynb` notebook.

## Web Application `EpiSim`
The web application can be run independently of the model. You can either 
build it using docker compose (recommended for production) or the built-in
Flask server (recommended for development).

### Build web app with docker compose
The web application can be built using docker compose using Nginx as the HTTP server 
and uWSGI as the application server.

To build the application, run

```shell
make build
```

or (similarly)
```shell
docker compose up --build -d
```

Go to http://localhost/4401.

### Run web app without build
Alternatively, you can also run the web app using the builtin server, which is not suitable for 
production but much simpler for development and test purposes.

```shell
make run
```

or (similarly)

```shell
python app/run.py
```

Go to http://localhost:4401
