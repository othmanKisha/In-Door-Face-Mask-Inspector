import os
import cmd
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

# # [IMPORTANT]
# # *** Here we should add all cameras ***
# # - IP Cameras should be added as follows:
# #   "rtsp://<ip>:<port>/h264_pcm.sdp"
# #   or 
# #   "rtsp://<ip>:<port>/h264_ulaw.sdp"
# #   - testing on ip webcam app for android
# #   - the app should be on the same network as the computer to identify it
CAMERAS = {
    "web_cam": 0,
    "office1": "rtsp://192.168.100.13:8080/h264_pcm.sdp"
}
