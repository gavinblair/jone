import subprocess
import json
import os

def get_sftp_credentials(site_slug, env_slug):
    command = f"terminus connection:info {site_slug}.{env_slug}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Error executing terminus command")
        return None

    output = result.stdout.strip()
    if not output:
        print("No output found from terminus command")
        return None

    # Look for the line that starts with "SFTP Command" and handle line wrapping
    lines = output.split('\n')
    sftp_details = []
    capture = False
    for line in lines:
        if 'SFTP Command' in line:
            capture = True
        if capture:
            # Append current line to sftp_details, stripping leading spaces and newlines
            sftp_details.append(line.strip())
        # Assuming the next section starts with "Git Command" or another recognizable line
        if 'Git Command' in line:
            break

    # Join the lines to form the complete command
    sftp_command_complete = ' '.join(sftp_details)
    # Extract the username and host using the expected format
    try:
        # The SFTP command line is expected to follow 'sftp -o Port=2222 user@host'
        parts = sftp_command_complete.split()
        username_host = parts[3]  # Adjust based on actual output structure
        username, host = username_host.split('@')

    except ValueError as e:
        print(f"Error parsing SFTP credentials: {e}")
        return None

    # todo: this should be stored in dotenv
    password = "your_password_here"  # Handle securely

    return {
        "host": host,
        "username": username,
        "password": password
    }



def create_vscode_sftp_json(site_slug, env_slug, sftp_credentials):
    vscode_folder_path = '.vscode'
    sftp_file_path = os.path.join(vscode_folder_path, 'sftp.json')

    if not os.path.exists(vscode_folder_path):
        os.makedirs(vscode_folder_path)
    
    sftp_config = {
        "name": f"{env_slug} on {site_slug}",
        "host": sftp_credentials["host"],
        "protocol": "sftp",
        "port": 2222,
        "username": sftp_credentials["username"],
        "password": sftp_credentials["password"],
        "remotePath": "/code/web/modules/custom/mms",
        "uploadOnSave": True,
        "useTempFile": False,
        "openSsh": False
    }

    with open(sftp_file_path, 'w') as file:
        json.dump(sftp_config, file, indent=4)

    print(f"sftp.json has been created/updated in {vscode_folder_path}")

# Example usage
site_slug = "cmhf"
env_slug = "gav-feb"

sftp_credentials = get_sftp_credentials(site_slug, env_slug)
if sftp_credentials:
    create_vscode_sftp_json(site_slug, env_slug, sftp_credentials)
