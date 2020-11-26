# In Door Face Mask Inspector (IDFMI) 
## Description
### 1. Overview
This is a project that aims to allow the return of working environment in indoor offices.

It focuses on reading live streams for ip cameras in enterprise environment,
after that, it applies a face mask detection model using the state-of-art Artificial Neural Networks.

In addition to detection, it also provides a customization platform for surveillence cameras.

Another service provided from the system is alerting security members via email. 
### 2. Project Architecture
The project consists of 3 containers

```bash
idfmi: Contains the Flask application and gunicorn application server
nginx: Contains the Nginx web server
mongo: Contains the MongoDB database
```

Some info about the stack used

```bash
Python version: 3.8.1
Web framework:  Flask
Database:       MongoDB (Using the pymongo driver)
App server:     gunicorn
Worker class:   gevent
Web server:     Nginx
Front end:      Bootsrap4, JQuery
```

The system Architecture of IDFMI

![System Architecture](https://github.com/othmanKisha/In-Door-Face-Mask-Inspector/blob/master/docs/system_architecture.PNG)
### 3. Project Tree
The following is how the files are structured inside the project:

    In-Door-Face-Mask-Inspector/
        .gitignore
        docker-compose.yml
        LICENSE
        README.md
        app/
            app.py
            camera.py
            config.py
            Dockerfile
            requirements.txt 
            model/
                face_mask_detection.pb
                load_model.py
                utils.py
            static/
                favicon.ico
                main.css     
                main.js   
                main.scss  
            templates/
                base.html
                auth_error.html 
                forms/
                   camera.html
                   security.html 
                pages/
                   home.html
                   welcome.html
        nginx/
            Dockerfile
            idfmi.conf
            nginx.conf
    
### 4. Screenshots
#### The home page before signing
- light theme 

![Welcome Page Light](https://github.com/othmanKisha/In-Door-Face-Mask-Inspector/blob/master/docs/welcome-light.PNG)

- dark theme 

![Welcome Page Dark](https://github.com/othmanKisha/In-Door-Face-Mask-Inspector/blob/master/docs/welcome-dark.PNG)
#### The home page after signing
- light theme 

![Demo](https://github.com/othmanKisha/In-Door-Face-Mask-Inspector/blob/master/docs/home-light.gif)

- dark theme 

![Home Page Dark](https://github.com/othmanKisha/In-Door-Face-Mask-Inspector/blob/master/docs/home-dark.gif)
#### Different functionalities

- Adding a camera

    - light theme 
    
    ![Create Camera Light](https://github.com/othmanKisha/In-Door-Face-Mask-Inspector/blob/master/docs/create-camera-light.PNG)

    - dark theme 

    ![Create Camera Dark](https://github.com/othmanKisha/In-Door-Face-Mask-Inspector/blob/master/docs/create-camera-dark.PNG)

- Adding a security member

    - light theme 

    ![Create Security Light](https://github.com/othmanKisha/In-Door-Face-Mask-Inspector/blob/master/docs/create-security-light.PNG)

    - dark theme 

    ![Create Security Dark](https://github.com/othmanKisha/In-Door-Face-Mask-Inspector/blob/master/docs/create-security-dark.PNG)

- View all security member

    - light theme 

    ![View Security Light](https://github.com/othmanKisha/In-Door-Face-Mask-Inspector/blob/master/docs/view-security-light.gif)

    - dark theme 

    ![View Security Dark](https://github.com/othmanKisha/In-Door-Face-Mask-Inspector/blob/master/docs/view-security-dark.gif)

- Update forms are similar to create forms.
#### Camera Stream and Detection 
- light theme 

![Detection Light](https://github.com/othmanKisha/In-Door-Face-Mask-Inspector/blob/master/docs/detection-light.gif)

- dark theme  

![Detection Dark](https://github.com/othmanKisha/In-Door-Face-Mask-Inspector/blob/master/docs/detection-dark.gif)
## Requirements
### 1. Docker
Since the project is containerized, then the only important dependency is to have docker and docker compose installed, installation guides are as follows:
- Docker Desktop for Windows: https://docs.docker.com/docker-for-windows/install/ 
- Docker Desktop for Mac OS: https://docs.docker.com/docker-for-mac/install/
- Docker Engine for linux: https://docs.docker.com/engine/install/
- Docker-Compose for linux: https://docs.docker.com/compose/install/

Notice that for Windows and Mac you should only install docker desktop, which will download docker engine and docker-compose by default.
### 2. Microsoft Azure Subscription 
This is a requirement for the demo only to simulate the working environment with respect to authentication, authorization, and Secrets.

You can check microsoft's documentation on how to make a project with azure active directory and keyvault.

- Azure Active Directory: https://azure.microsoft.com/en-us/services/active-directory/#documentation

- Azure KeyVault: https://azure.microsoft.com/en-us/services/key-vault/#documentation
### 3. Email Account
- could any email (gmail, yahoo, outlook), but we used gmail for our prototype.
## Installation
- clone the repository:

    ```bash
    git clone https://github.com/othmanKisha/In-Door-Face-Mask-Inspector.git
    ```   
- After finishing all the steps for Azure Active Directory and Key Vault, make sure to add a **.env** file and inside the file add the following:
    ```bash
    KEY_VAULT_NAME=${KEY_VAULT_NAME} # Stored in OS environment
    AZURE_CLIENT_ID=${AZURE_CLIENT_ID} # Stored in OS environment
    AZURE_CLIENT_SECRET=${AZURE_CLIENT_SECRET} # Stored in OS environment
    AZURE_SUBSCRIPTION_ID=${AZURE_SUBSCRIPTION_ID} # Stored in OS environment
    AZURE_TENANT_ID=${AZURE_TENANT_ID} # Stored in OS environment
    MONGODB_DATABASE=<The name of the database to be created>
    MONGODB_USERNAME=<The username of the database to be created>
    MONGODB_PASSWORD=<The password of the database to be created>
    MONGODB_HOSTNAME=mongodb # This is the name of mongodb container
    EMAIL_ADDRESS=<The email address created to send alerts>
    EMAIL_PASSWORD=<The password of the alerts email address>
    SMTP_SERVER=<The mail server, it is smtp.gmail.com when you use gmail, you can search the other mail servers>
    ```
## Usage
- after cloning the repo, go to the project directory:

    ```bash
    cd In-Door-Face-Mask-Inspector
    ```
- run docker-compose command:

    ```bash
    docker-compose up -d
    ```
- now you can view the website by typing `localhost` on the browser.   
## Acknowledgment
- Face Mask Detection Model by [AIZOOTech](https://github.com/AIZOOTech)

    Link: https://github.com/AIZOOTech/FaceMaskDetection
- Camera Streaming with Flask by [Miguel Grinberg](https://github.com/miguelgrinberg)

    Link: https://github.com/miguelgrinberg/flask-video-streaming
- Azure Active Directory with Flask by [René Bremer](https://github.com/rebremer)

    Link:https://github.com/rebremer/ms-identity-python-webapp-backend
## Authors
- [Abdullah Alnasser](https://github.com/Alnasser0)

- [Mahmoud Ellouh](https://github.com/Mellouh255)

- [Othman Kisha](https://github.com/othmanKisha)    
## License
[MIT](https://github.com/othmanKisha/In-Door-Face-Mask-Inspector/blob/master/LICENSE)