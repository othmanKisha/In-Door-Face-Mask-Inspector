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

![System Architecture](images/system_architecture.png)
### 3. Project Tree
The following is how the files are structured inside the project:

    In-Door-Face-Mask-Inspector/
    │   .dockerignore    
    │   .gitignore
    │   docker-compose.yml
    │   Dockerfile
    │   LICENSE
    │   README.md
    │   requirements.txt
    ├───app/
    │   │   app.py
    │   │   auth.py
    │   │   camera.py
    │   │   config.py
    │   ├───model/
    │   │       face_mask_detection.pb
    │   │       load_model.py
    │   │       utils.py
    │   ├───static/
    │   │       main.css   
    │   │       icon.png   
    │   │       main.js   
    │   │       main.scss      
    │   └───templates/
    │       │   base.html
    │       │   auth_error.html        
    │       ├───forms/
    │       │       camera.html
    │       │       security.html        
    │       └───pages/
    │               home.html
    │               welcome.html
    ├───gunicorn/
    │       gunicorn.conf.py
    └───nginx/
            nginx.conf
    
### 4. Screenshots
#### The home page before signing
- light theme 
![Welcome Page Light](images/welcome-light.png)
- dark theme 
![Welcome Page Dark](images/welcome-dark.png)
#### The home page after signing
- light theme 
![Home Page Light](images/home-light.png)
- dark theme 
![Home Page Dark](images/home-dark.png)
#### Different functionalities

- Adding a camera
    - light theme 
    ![Create Camera Light](images/create-camera-light.png)

    - dark theme 
    ![Create Camera Dark](images/create-camera-dark.png)

- Adding a security member
    - light theme 
    ![Create Security Light](images/create-security-light.png)

    - dark theme 
    ![Create Security Dark](images/create-security-dark.png)

- View all security member
    - light theme 
    ![View Security Light](images/view-security-light.png)

    - dark theme 
    ![View Security Dark](images/view-security-dark.png)

- Update forms are similar to create forms.
#### Camera Stream and Detection 
- light theme 
![Detection Light](images/detection-light.gif)
- dark theme  
![Detection Dark](images/detection-dark.gif)
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

## Installation
- clone the repository:

    ```bash
    git clone https://github.com/othmanKisha/In-Door-Face-Mask-Inspector.git
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