from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from tensorflow.keras.models import load_model
from pymongo import MongoClient
import cv2
import os


keyVaultName = os.environ["KEY_VAULT_NAME"]
KeyVaultUri = f"https://{keyVaultName}.vault.azure.net"
credential = DefaultAzureCredential()
client = SecretClient(
    vault_url=KeyVaultUri,
    credential=credential
)


# The Client ID for azure active directory
CLIENT_ID = client.get_secret("CLIENT-ID").value

# In a production app, we recommend you use a more secure method of 
# storing your secret, like Azure Key Vault. 
# Or, use an environment variable as described in Flask's documentation:
# https://flask.palletsprojects.com/en/1.1.x/config/#configuring-from-environment-variables
CLIENT_SECRET = client.get_secret("CLIENT-SECRET").value

# For multi-tenant app
# AUTHORITY = "https://login.microsoftonline.com/Enter_the_Tenant_Name_Here"
AUTHORITY = "https://login.microsoftonline.com/29b4b088-d27d-4129-b9f9-8637b59ea4b3"

# Used for forming an absolute URL to your redirect URI.
# The absolute URL must match the redirect URI you set
# in the app's registration in the Azure portal.
REDIRECT_PATH = "/getAToken"

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
# This resource requires no admin consent
ENDPOINT = 'https://graph.microsoft.com/v1.0/users'

# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["User.ReadBasic.All"]

# Specifies the token cache should be stored in server-side session
SESSION_TYPE = "filesystem"


# Database username
# Passed with the environment for docker
userDB = os.environ['MONGODB_USERNAME'] 

# Database password
# Passed with the environment for docker
passDB = os.environ['MONGODB_PASSWORD']

# The hostname of the server that hosts the database
# Passed with the environment for docker
hostDB = os.environ['MONGODB_HOSTNAME'] 

# The port at which the database is running
portDB = 27017

# The name of the database
# Passed with the environment for docker
nameDB = os.environ['MONGODB_DATABASE']

# Connecting with mongodb
cluster = MongoClient(
    host=hostDB, 
    port=portDB, 
    username=userDB, 
    password=passDB
)


# Assigning the db using the db name
db = cluster[nameDB]

# The default confidence of the model
CONFIDENCE = 0.5

# The directory containing the models
modelsDirectory = "models"

# The directory containing the models for face detector
faceDetector = "face_detector"

# The directory containing the models for mask detector
maskDetector = "mask_detector"

# The file that contains the weights for the face detector
weightsFile = "res10_300x300_ssd_iter_140000.caffemodel"

# The file that contains the prototxt for the face detector
prototxtFile = "deploy.prototxt"

# The file that contains the mask detector model
modelFile = "mask_detector.model"

# The face detector model
FACE_NET = cv2.dnn.readNet(
    os.path.sep.join([
        modelsDirectory,
        faceDetector, 
        prototxtFile
    ]),
    os.path.sep.join([
        modelsDirectory, 
        faceDetector, 
        weightsFile
    ])
)


# The mask detector model
MASK_NET = load_model(os.path.sep.join([
    modelsDirectory, 
    maskDetector, 
    modelFile
]))


# The email for the mail server
EMAIL = ""

# The password of the mail server
EMAIL_PASSWORD = ""

# SMS Client id
SMS_CLIENT_ID = ""

# SMS secret
SMS_SECRET = ""

# SMS Base phone number
SMS_PHONE_NUMBER = ""
