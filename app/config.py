import os
import cmd
from pymongo import MongoClient
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential


keyVaultName = os.environ["KEY_VAULT_NAME"]
KVUri = f"https://{keyVaultName}.vault.azure.net"

credential = DefaultAzureCredential()
client = SecretClient(vault_url=KVUri, credential=credential)

CLIENT_ID = client.get_secret("CLIENT-ID").value # Application (client) ID of app registration

CLIENT_SECRET = client.get_secret("CLIENT-SECRET").value # Placeholder - for use ONLY during testing.
# In a production app, we recommend you use a more secure method of storing your secret,
# like Azure Key Vault. Or, use an environment variable as described in Flask's documentation:
# https://flask.palletsprojects.com/en/1.1.x/config/#configuring-from-environment-variables
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# if not CLIENT_SECRET:
#     raise ValueError("Need to define CLIENT_SECRET environment variable")

# For multi-tenant app
AUTHORITY = "https://login.microsoftonline.com/29b4b088-d27d-4129-b9f9-8637b59ea4b3"  
# AUTHORITY = "https://login.microsoftonline.com/Enter_the_Tenant_Name_Here"

REDIRECT_PATH = "/getAToken"  # Used for forming an absolute URL to your redirect URI.
                              # The absolute URL must match the redirect URI you set
                              # in the app's registration in the Azure portal.

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
ENDPOINT = 'https://graph.microsoft.com/v1.0/users'  # This resource requires no admin consent

# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["User.ReadBasic.All"]

SESSION_TYPE = "filesystem"  # Specifies the token cache should be stored in server-side session

# Initiating the mongo client
client = MongoClient(
    host=os.environ['MONGODB_HOSTNAME'], # taken from environment variable passed from the compose
    port=int(os.environ['MONGODB_PORT']), # taken from environment variable passed from the compose
    username=os.environ['MONGODB_USERNAME'], # taken from environment variable passed from the compose
    password=os.environ['MONGODB_PASSWORD'] # taken from environment variable passed from the compose
)

# Connecting with the idfmiDB
db = client[os.environ['MONGODB_DATABASE']] # taken from environment variable passed from the compose

# db.cameras.insert_many([
#     {"office": "1", "label": "#1", "RTSP": "rtsp://192.168.100.13:8080/h264_pcm.sdp"},
#     {"office": "2", "label": "#2", "RTSP": "rtsp://192.168.100.13:8080/h264_pcm.sdp"},
#     {"office": "3", "label": "#3", "RTSP": "rtsp://192.168.100.13:8080/h264_pcm.sdp"},
#     {"office": "4", "label": "#4", "RTSP": "rtsp://192.168.100.13:8080/h264_pcm.sdp"},
#     {"office": "5", "label": "#5", "RTSP": "rtsp://192.168.100.13:8080/h264_pcm.sdp"},
#     {"office": "6", "label": "#6", "RTSP": "rtsp://192.168.100.13:8080/h264_pcm.sdp"},
#     {"office": "7", "label": "#7", "RTSP": "rtsp://192.168.100.13:8080/h264_pcm.sdp"},
#     {"office": "8", "label": "#8", "RTSP": "rtsp://192.168.100.13:8080/h264_pcm.sdp"},
#     {"office": "9", "label": "#9", "RTSP": "rtsp://192.168.100.13:8080/h264_pcm.sdp"}
# ])