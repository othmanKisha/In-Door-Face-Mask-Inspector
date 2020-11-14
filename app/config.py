from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from tensorflow.keras.models import load_model
from pymongo import MongoClient
from smtplib import SMTP
import cv2
import os


SESSION_TYPE = "filesystem"  # for sessions
SECRET_KEY = b'\xd6\x04\xbdj\xfe\xed$c\x1e@\xad\x0f\x13,@G'  # used for the forms

# [keyvault config]
KEY_VAULT_NAME = os.environ["KEY_VAULT_NAME"]
TENANT_ID = os.environ["AZURE_TENANT_ID"]
KVUri = f"https://{KEY_VAULT_NAME}.vault.azure.net"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=KVUri, credential=credential)
CLIENT_ID = client.get_secret("CLIENT-ID").value
CLIENT_SECRET = client.get_secret("CLIENT-SECRET").value
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
ENDPOINT = 'https://graph.microsoft.com/v1.0/users'
# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["User.ReadBasic.All"]
# Used for forming an absolute URL to your redirect URI.
# The absolute URL must match the redirect URI you set
# in the app's registration in the Azure portal.
REDIRECT_PATH = "/getAToken"

# [mongo database config]
DB_USER = os.environ['MONGODB_USERNAME']
DB_PASS = os.environ['MONGODB_PASSWORD']
DB_HOST = os.environ['MONGODB_HOSTNAME']
DB_NAME = os.environ['MONGODB_DATABASE']
DB_PORT = 27017
cluster = MongoClient(
    host=DB_HOST, port=DB_PORT,
    username=DB_USER, password=DB_PASS)
db = cluster[DB_NAME]

# [mail config]
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
SMTP_SERVER = os.environ["SMTP_SERVER"]
SMTP_PORT = 587
smtp = SMTP(SMTP_SERVER, SMTP_PORT)

# [model config]
CONFIDENCE = 0.5
DIR = "models"
FACE = "face_detector"
MASK = "mask_detector"
WEIGHTS = "res10_300x300_ssd_iter_140000.caffemodel"
PROTOTXT = "deploy.prototxt"
MODEL = "mask_detector.model"
faceNet = cv2.dnn.readNet(
    os.path.sep.join([DIR, FACE, PROTOTXT]),
    os.path.sep.join([DIR, FACE, WEIGHTS]))
maskNet = load_model(os.path.sep.join([DIR, MASK, MODEL]))
