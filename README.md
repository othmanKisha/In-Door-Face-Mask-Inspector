# IDFMI - Coming Project Tasks

## Authentication (**DONE**)
- Store all program keys with either Azure Vault or in a file between the team.
### Azure Key Vault
- key management.

## Database
- Alerts and Saving photos should be done in parallel, and there should be a timer for 2s between each alert.
### Alerts
- If there is a violation for *Threshold* (0.7) or above, send an email to the security. Indicating violation information embedded with an image.
- Learn how to send email from python automatically.
### Saving Violation Photos
- Get frame, check with the *threshold*, store in the database if *prediction* equal to or more than the *threshold*.

## Backend
- Connect the backend to key vault and the database. (**DONE**)
### Gunicorn
- Configuring gunicorn with the backend.

## Frontend 
Will use various templates from the internet.
### Login Page
### Customization Page
### Administrator Page

## Others
### Containerization (**DONE**)
- To use the system locally just type:

    `python app\app.py`
### Costumization
- Dynamic or Static.
- Inside the program or After deployment.
### Performance Testing
- Multi-threading.