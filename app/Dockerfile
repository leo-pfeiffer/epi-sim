# Use the Python3.9 image
FROM python:3.9-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD /app /app

# Install the dependencies
ADD app/requirements.txt app/requirements.txt
RUN pip install -r requirements.txt

# run the command to start uWSGI
CMD ["uwsgi", "app.ini"]