import requests

def download_file(download_url: str, save_path: str):
    '''Download a file from url and save it to given path.'''
    print(f'Downloading file from {download_url}...')
    downloaded_data = requests.get(download_url).content
    with open(save_path, 'wb') as file:
        file.write(downloaded_data)
