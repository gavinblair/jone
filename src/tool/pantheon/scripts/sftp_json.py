import subprocess
import json
import os
from dotenv import load_dotenv

# Determine the directory in which the script resides
script_directory = os.path.dirname(os.path.realpath(__file__))
env_path = os.path.join(script_directory, '.env')

# Load environment variables from .env file located in the script's directory
load_dotenv(dotenv_path=env_path)

def get_terminus_field(site_slug, env_slug, field_name):
    """Execute terminus command to get a specific field value."""
    command = f"terminus connection:info {site_slug}.{env_slug} --field={field_name}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error executing terminus command for {field_name}")
        print(result)
        return None

    # Extract the actual value, which is after the last newline
    output_lines = result.stdout.strip().split('\n')
    actual_value = output_lines[-1].strip()  # Get the last line which should be the value
    return actual_value

def get_sftp_credentials(site_slug, env_slug):
    # Use the helper function to get username and host
    username = get_terminus_field(site_slug, env_slug, 'sftp_username')
    host = get_terminus_field(site_slug, env_slug, 'sftp_host')

    if username is None or host is None:
        return None

    # Retrieve password from .env file or another secure location
    password = os.getenv('PANTHEON_PASSWORD', 'default_password_if_not_set')

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
        "remotePath": "/code/web/modules/custom/",
        "uploadOnSave": True,
        "useTempFile": False,
        "openSsh": False
    }

    with open(sftp_file_path, 'w') as file:
        json.dump(sftp_config, file, indent=4)

    print(f"sftp.json has been created/updated in {vscode_folder_path}")
# Example usage, parsing command line arguments for site_slug and env_slug
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate VSCode sftp.json configuration from Terminus.")
    parser.add_argument("site_slug", help="Site slug for the Pantheon site")
    parser.add_argument("env_slug", help="Environment slug for the site environment")
    args = parser.parse_args()

    sftp_credentials = get_sftp_credentials(args.site_slug, args.env_slug)
    if sftp_credentials:
        create_vscode_sftp_json(args.site_slug, args.env_slug, sftp_credentials)