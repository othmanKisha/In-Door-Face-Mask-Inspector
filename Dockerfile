FROM python:3.8.1

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install requirements using pip
RUN pip install --upgrade pip
COPY ./requirements.txt /
RUN pip install -r requirements.txt

# Adding the app files
COPY ./app /app

# Setting the working directory
WORKDIR /app

# Expossing ports
EXPOSE 5000