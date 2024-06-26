# Use the official Ubuntu base image
FROM ubuntu:22.04

# Update packages and install necessary dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install dependencies
RUN pip3 install -r requirements.txt
# RUN pip3 install Flask-MySQL SQLAlchemy mysql-connector-python

RUN pip3 install Werkzeug==2.3.6

# Copy the entire current directory into the container at /app
COPY ./app /app/
WORKDIR /app