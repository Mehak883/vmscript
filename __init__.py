import logging
import datetime
import requests
from azure.identity import DefaultAzureCredential

# 🔧 Set these values
subscription_id = "461cd049-fd4b-4431-87b3-5b7e956bf416"
resource_group = "rg-demo-dev-001"
vm_name = "vm-demo-dev-001"
blob_url = "https://stdemodev045.blob.core.windows.net/scriptctnr/run_myscript.bat?sp=r&st=2025-07-12T13:16:22Z&se=2025-07-12T21:16:22Z&spr=https&sv=2024-11-04&sr=b&sig=vgDHgnSatAAn3aGxw1A9YCYdPXurwvFJonbm0fEFJFo%3D"

def main(mytimer):
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    logging.info(f"Timer function triggered at {utc_timestamp}")

    try:
        # Get Azure access token
        credential = DefaultAzureCredential()
        token = credential.get_token("https://management.azure.com/.default").token

        # Prepare the PowerShell script to run on VM
        powershell_script = f"""
        Invoke-WebRequest -Uri '{blob_url}' -OutFile 'C:\\run_myscript.bat'
        Start-Process -FilePath 'C:\\run_myscript.bat' -NoNewWindow -Wait
        """

        # Azure REST API for Run Command
        url = (
            f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
            f"/providers/Microsoft.Compute/virtualMachines/{vm_name}/runCommand?api-version=2021-11-01"
        )

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "commandId": "RunPowerShellScript",
            "script": [powershell_script]
        }

        # Run the command on VM
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code in [200, 202]:
            logging.info("Batch file downloaded and executed successfully on the VM.")
        else:
            logging.error(f"Failed to run script: {response.status_code} - {response.text}")

    except Exception as e:
        logging.exception(f"Exception while running script on VM: {str(e)}")
