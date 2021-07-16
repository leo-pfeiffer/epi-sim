# Python 3.9 image
FROM python:3.9-buster

# Set working directory to /app
WORKDIR /app

# Copy current directory contents into container at /app
ADD . /app

# Install requirements
RUN pip install -r requirements.txt

# run the command to start uWSGI
CMD ["uwsgi", "app.ini"]