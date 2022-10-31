import requests

def download_file(download_url: str, save_path: str) -> None:
    '''Download a file from url and save it to given path.'''
    print(f'Downloading file from {download_url}...')
    downloaded_data = requests.get(download_url).content
    with open(save_path, 'wb') as file:
        file.write(downloaded_data)

def find_release(repo_link: str, tag: str) -> str:
    response = requests.get(repo_link)
    releases = response.json()
    for release in releases:
        if release['target_commitish'] == tag:
            link = release['zipball_url']
            return link