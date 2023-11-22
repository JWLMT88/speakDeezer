import os
import requests
import ctypes
from datetime import datetime
from tqdm import tqdm
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

def check_update_and_download(repo_owner, repo_name, file_path, download_path=None, overwrite=False):
    try:
        if not all([repo_owner, repo_name, file_path]):
            raise ValueError('Not all required parameters were passed.')

        # GitHub API endpoint for the repository
        api_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/commits'

        # Query the latest commits
        response = requests.get(api_url)
        response.raise_for_status()

        # Get the SHA of the latest commit
        latest_sha = response.json()[0]['sha']

        # Query file metadata
        api_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}?ref={latest_sha}'
        response = requests.get(api_url)
        response.raise_for_status()
        file_metadata = response.json()

        # Check if the file has been updated
        if os.path.isfile(file_path):
            local_mtime = os.path.getmtime(file_path)
            github_mtime = datetime.strptime(file_metadata['last_modified'], '%Y-%m-%dT%H:%M:%SZ').timestamp()
            if local_mtime >= github_mtime:
                print('File is up to date.')
                return
            elif not overwrite:
                print('Local file is outdated. Set "overwrite" to True to update it.')
                return
        else:
            print('Local file not found.')

        # Download the latest version of the file
        download_url = file_metadata['download_url']
        response = requests.get(download_url, stream=True)
        response.raise_for_status()

        # Determine the download path
        if download_path is None:
            download_path = file_path
        else:
            download_path = os.path.join(download_path, os.path.basename(file_path))

        if not overwrite and os.path.isfile(download_path):
            print('File already exists. Set "overwrite" to True to overwrite it.')
            return

        # Get the file size for progress bar
        file_size = int(response.headers.get('content-length', 0))

        # Start downloading with progress bar
        progress_bar = tqdm(total=file_size, unit='B', unit_scale=True)
        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
                progress_bar.update(len(chunk))
        progress_bar.close()

        print(f'File has been updated and downloaded to: {download_path}')
    except requests.exceptions.RequestException as e:
        print(f'Error making request to GitHub API: {e}')
    except ValueError as ve:
        print(f'Error: {ve}')
    except Exception as ex:
        print(f'An unexpected error occurred: {ex}')