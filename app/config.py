from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from model.load_model import load_tf_model
from model.utils import generate_anchors
from pymongo import MongoClient
from smtplib import SMTP
import numpy as np
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
DIR = "model"
MODEL = "face_mask_detection.pb"
SESS, GRAPH = load_tf_model(os.path.join(DIR, MODEL))
# anchor configuration
feature_map_sizes = [[33, 33], [17, 17], [9, 9], [5, 5], [3, 3]]
anchor_sizes = [[0.04, 0.056], [0.08, 0.11], [0.16, 0.22], [0.32, 0.45], [0.64, 0.72]]
anchor_ratios = [[1, 0.62, 0.42]] * 5
# generate anchors
anchors = generate_anchors(feature_map_sizes, anchor_sizes, anchor_ratios)
# for inference , the batch size is 1, the model output shape is [1, N, 4],
# so we expand dim for anchors to [1, anchor_num, 4]
ANCHORS_EXP = np.expand_dims(anchors, axis=0)
ID2CLASS = {0: 'Mask', 1: 'NoMask'}
