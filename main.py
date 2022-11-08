"""
Usage: Run the script and optionally add commandline arguments to it. Default
configuration (no arguments) downloads the stable version of packs.

--skip_download
--download_mode ["stable" or "preview"]


Examples:
    Downloading preview packs and extracting data from them:
        python main.py --download_mode preview

    Downloading packs from custom urls
        python main--repo_url example.com

The scripts uses temporary path `packs`. The path is not cleared after the
execution, it conditionally removed and added again at the start of the script.
"""

import wiki_tools
import wiki_content_generator as wcg
from tkinter import filedialog
from os import get_handle_inheritable, path, makedirs, listdir, chdir
from downloader import download_file, find_release
from zipfile import ZipFile
import sys
import shutil


def launch() -> None:
    print('Welcome to Bedrock Wiki Content Generator!')
    argv = sys.argv
    global DOWNLOAD_MODE, SKIP_DOWNLOAD, DOWNLOAD_LINK, VERSION_TAG

    if '--download_mode' in argv and len(argv) > argv.index('--download_mode'):
        DOWNLOAD_MODE = argv[argv.index('--download_mode')+1]
    else:
        DOWNLOAD_MODE = 'stable'
    if DOWNLOAD_MODE in ['stable', 'preview']:
        VERSION_TAG = {'stable': 'main', 'preview': 'preview'}[DOWNLOAD_MODE]
        DOWNLOAD_LINK = find_release('https://api.github.com/repos/Mojang/bedrock-samples/releases?per_page=10&page=1', VERSION_TAG)
    else:
        print(f'Unknown download mode {DOWNLOAD_MODE}.')
        exit()

    SKIP_DOWNLOAD = '--skip_download' in argv
    main()


def main() -> None:
    # Set some variables
    chdir(path.dirname(path.realpath(__file__)))
    rp_path = path.join('packs', 'resource_pack')
    bp_path = path.join('packs', 'behavior_pack')
    repo_save_path = path.join('packs', 'vp.zip')
    wiki_path_file = 'wiki_local_path.txt'
    is_stable = DOWNLOAD_MODE == 'stable'
    custom_data_path = 'custom_data'
    test_page_path = 'test-page.md'
    
    # Download & extract packs
    if not SKIP_DOWNLOAD:
        shutil.rmtree('packs', True)
        makedirs('packs', exist_ok=True)

        print('Downloading files...')
        download_file(DOWNLOAD_LINK, repo_save_path)
        print('Downloaded!')

    print('Extracting files...')
    with ZipFile(repo_save_path) as unzipping_file:
        unzipping_file.extractall('packs')
    print('Extracted!')

    packs_contents = listdir('packs')
    if 'vp.zip' in packs_contents:
        packs_contents.remove('vp.zip')
    extracted_folder = packs_contents[0]

    print('Copying packs...')
    shutil.move(path.join('packs', extracted_folder, 'behavior_pack'), 'packs')
    shutil.move(path.join('packs', extracted_folder, 'resource_pack'), 'packs')
    print('Copied!')

    shutil.rmtree(path.join('packs', extracted_folder))

    # Extract custom data
    for element in listdir('custom_data'):
        if not element.endswith('.zip'):
            shutil.rmtree(path.join('custom_data', element))
        else:
            with ZipFile(path.join('custom_data', element)) as unzipping_file:
                unzipping_file.extractall(path.join('custom_data', element.replace('.zip', '')))

    # Wiki repo folder local path
    if path.exists(wiki_path_file):
        with open(wiki_path_file, 'r+') as wiki_path_file:
            wiki_path = wiki_path_file.readline()
        if wiki_path == '':
            print('Select Wiki repository folder')
            wiki_path = filedialog.askdirectory()
            wiki_path_file.write(wiki_path)
    else:
        print('Select Wiki repository folder')
        with open(wiki_path_file, 'w') as wiki_path_file:
            wiki_path = filedialog.askdirectory()
            wiki_path_file.write(wiki_path)

    # Content generation
    print('---')
    version = wcg.get_version(rp_path, is_stable)
    custom_data_version = wcg.get_custom_data_version()
    wiki_tools.upload_content(path.join(wiki_path, 'docs', 'blocks', 'block-sounds.md'), wcg.get_block_sounds(rp_path, version)) # block sounds
    wiki_tools.upload_content(path.join(wiki_path, 'docs', 'commands', 'nbt-commands.md'), wcg.can_place_on_everything(rp_path, version)) # can_place_on_everything
    wiki_tools.upload_content(path.join(wiki_path, 'docs', 'documentation', 'creative-categories.md'), wcg.get_creative_categories_table(rp_path, version)) # creative categories
    wiki_tools.upload_content(path.join(wiki_path, 'docs', 'documentation', 'fog-ids.md'), wcg.get_fogs_table(rp_path, version)) # fog ids
    wcg.generate_sound_definitions(rp_path, version, path.join(wiki_path, 'docs', 'documentation', 'sound-definitions.md')) # sound definitions
    wcg.generate_biome_tags_tables(path.join(custom_data_path, 'biomes'), custom_data_version, path.join(wiki_path, 'docs', 'world-generation', 'biome-tags.md')) # biome and tags tables
    wcg.generate_vu_spawn_rules(bp_path, version, path.join(wiki_path, 'docs', 'entities', 'vanilla-usage-spawn-rules.md'), 8) # vanilla usage spawn rules
    wcg.generate_vu_spawn_rules(bp_path, version, path.join(wiki_path, 'docs', 'entities', 'vusr-full.md'), -1) # full vanilla usage spawn rules
    wcg.generate_vu_items(bp_path, version, path.join(wiki_path, 'docs', 'items', 'vanilla-usage-items.md'), 8) # vanilla usage items
    wcg.generate_vu_items(bp_path, version, path.join(wiki_path, 'docs', 'items', 'vui-full.md'), -1) # full vanilla usage items
    wcg.generate_vu_entities(bp_path, version, path.join(wiki_path, 'docs', 'entities', 'vanilla-usage-components.md'), 8, 3) # vanilla usage entities
    wcg.generate_vu_entities(bp_path, version, path.join(wiki_path, 'docs', 'entities', 'vuc-full.md'), -1, -1) # full vanilla usage entities
    print(version)

    # Remove files
    shutil.rmtree(rp_path)
    shutil.rmtree(bp_path)
    print('Finished!')


if __name__ == "__main__":
    launch()