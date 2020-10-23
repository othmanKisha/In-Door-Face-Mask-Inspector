import os
import cmd
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

keyVaultName = os.environ["KEY_VAULT_NAME"]
KVUri = f"https://{keyVaultName}.vault.azure.net"

credential = DefaultAzureCredential()
client = SecretClient(vault_url=KVUri, credential=credential)

#secretName = input("Input a name for your secret > ")
#secretValue = input("Input a value for your secret > ")

#print(f"Creating a secret in {keyVaultName} called '{secretName}' with the value '{secretValue}' ...")

#client.set_secret(secretName, secretValue)

#print(" done.")

print(client.get_secret("CLIENT-ID"))
print(client.get_secret("CLIENT-SECRET"))

# print(f"Deleting your secret from {keyVaultName} ...")

# poller = client.begin_delete_secret(secretName)
# deleted_secret = poller.result()

print(" done.")