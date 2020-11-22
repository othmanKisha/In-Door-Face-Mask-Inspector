FROM python:3.8.1

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copying the requirements file
COPY requirements.txt /requirements.txt
# Upgrading pip
RUN pip3 install --upgrade pip
# Installing the requirements
RUN pip3 install -r ./requirements.txt

# Adding the app files
COPY . /app
# Setting the working directory
WORKDIR /app

# Exposing port 5000
EXPOSE 5000

# Running Gunicorn
ENTRYPOINT ["gunicorn", \
            "--bind", "0.0.0.0:5000", \
            "--workers", "1", \
            "--worker-class", "egg:meinheld#gunicorn_worker", \
            "--threads", "9", \
            "--timeout", "120", \
            "app:app"]