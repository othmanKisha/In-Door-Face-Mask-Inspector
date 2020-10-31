FROM python:3.8.1

# Copying the entrypoint shell script file
COPY ./entrypoint.sh /
# Changing the permissions for the entrypoint file
RUN chmod +x ./entrypoint.sh

# Copying the requirements file
COPY ./requirements.txt /
# Upgrading pip
RUN pip3 install --upgrade pip
# Installing the requirements
RUN pip3 install -r requirements.txt

# Adding the app files
COPY ./app /app
# Setting the working directory
WORKDIR /app

# Exposing port 5000
EXPOSE 5000
# Running Gunicorn
ENTRYPOINT ["sh", "/entrypoint.sh"]