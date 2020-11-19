# In Door Face Mask Inspector (IDFMI) 
## Description
### Overview
### Project Tree

    In-Door-Face-Mask-Inspector/
    │   .gitignore
    │   docker-compose.yml
    │   Dockerfile
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
    
## Requirements
### Docker
Since the project is containerized, then the only important dependency is to have docker and docker compose installed, installation guides are as follows:
- Docker Desktop for Windows: https://docs.docker.com/docker-for-windows/install/ 
- Docker Desktop for Mac OS: https://docs.docker.com/docker-for-mac/install/
- Docker Engine for linux: https://docs.docker.com/engine/install/
- Docker-Compose for linux: https://docs.docker.com/compose/install/

Notice that for Windows and Mac you should only install docker desktop, which will download docker engine and docker-compose by default.
### Microsoft Azure Subscription
This is a requirement for the demo only to simulate the working environment with respect to authentication, authorization, and Secrets.

- Azure Active Directory
- Azure KeyVault

You can check microsoft's documentation on how to make a project with azure active directory and keyvault.

## Installation
- clone the repository:

    ```bash
    git clone https://github.com/othmanKisha/In-Door-Face-Mask-Inspector.git
    ```   
## Usage
- after cloning the repo, go to the project directory:

    ```bash
    cd In-Door-Face-Mask-Inspector-master
    ```
- run docker-compose command:

    ```bash
    docker-compose up -d
    ```
- now you can view the website by typing `localhost` on the browser.   
## Authors
### [Abdullah Alnasser](https://github.com/Alnasser0)

### [Mahmoud Ellouh](https://github.com/Mellouh255)

### [Othman Kisha](https://github.com/othmanKisha)
## Acknowledgment
- Face Mask Detection Model by [AIZOOTech](https://github.com/AIZOOTech)

    Link: https://github.com/AIZOOTech/FaceMaskDetection
- Camera Streaming with Flask by [Miguel Grinberg](https://github.com/miguelgrinberg)

    Link: https://github.com/miguelgrinberg/flask-video-streaming
- Azure Active Directory with Flask by [René Bremer](https://github.com/rebremer)

    Link:https://github.com/rebremer/ms-identity-python-webapp-backend
## License
### [MIT](https://github.com/othmanKisha/In-Door-Face-Mask-Inspector/blob/master/LICENSE)