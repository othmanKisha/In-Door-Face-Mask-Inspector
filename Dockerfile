FROM python:3.8.1

# Copying the gunicorn configuration file
COPY ./gunicorn/gunicorn.conf.py /gunicorn.conf.py

# Copying the requirements file
COPY requirements.txt /requirements.txt
# Upgrading pip
RUN pip3 install --upgrade pip
# Installing the requirements
RUN pip3 install -r ./requirements.txt

# Adding the app files
COPY ./app /app
# Setting the working directory
WORKDIR /app

# Exposing port 5000
EXPOSE 5000

# Running Gunicorn
ENTRYPOINT ["gunicorn", "--config", "/gunicorn.conf.py", "app:app"]