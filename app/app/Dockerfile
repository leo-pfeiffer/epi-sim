# Python 3.9 image
FROM python:3.9-buster

# Set working directory to /app
WORKDIR /app

# Copy current directory contents into container at /app
ADD . /app

# Install pip requirements
RUN pip install --upgrade pip
RUN pip install -U setuptools wheel
RUN pip install -U -r requirements.txt

# start uWSGI
CMD ["uwsgi", "app.ini"]