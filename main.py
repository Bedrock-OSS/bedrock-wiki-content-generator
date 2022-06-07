"""
Usage: Run the script and optionally add commandline arguments to it. Default
configuration (no arguments) downloads the stable version of packs.

--skip_download
--download_mode ["stable" or "beta"]
--rp_url <the url to download resourcepack>
--bp_url <the url to download behaviorpack>

`--skip_download` also removes pack extraction.

Examples:
    Downloading beta packs and extracting data from them:
        python main.py --download_mode beta

    Downloading packs from custom urls
        python main --bp_url example.com --rp_url example1.com

The scripts uses temporary path `packs`. The path is not cleared after the
execution, it conditionally removed and added again at the start of the script.
"""
import wiki_tools
import wiki_content_generator as wcg
from tkinter import filedialog
import os
import downloader
from zipfile import ZipFile
import sys
import shutil


print('Welcome to Bedrock Wiki Content Generator!')

argv = sys.argv

try:
    DOWNLOAD_MODE = argv[argv.index('--download_mode')+1]
except:
    DOWNLOAD_MODE = 'stable'

if DOWNLOAD_MODE == 'stable':
    RP_URL = 'https://aka.ms/resourcepacktemplate'
    BP_URL = 'https://aka.ms/behaviorpacktemplate'
elif DOWNLOAD_MODE == 'beta':
    RP_URL = 'https://aka.ms/MinecraftBetaResources'
    BP_URL = 'https://aka.ms/MinecraftBetaBehaviors'
else:
    raise Exception(f'Unknown download mode {DOWNLOAD_MODE}.')

try:
    RP_URL = argv[argv.index('--rp_url')+1]
except:
    pass

try:
    RP_URL = argv[argv.index('--rp_url')+1]
except:
    pass

SKIP_DOWNLOAD = '--skip_download' in argv


def main():
    # Download & extract packs
    if not SKIP_DOWNLOAD:
        if os.path.exists('packs'):
            shutil.rmtree('packs')
        os.makedirs('packs', exist_ok=True)

        print('Downloading files...')
        downloader.download_file(RP_URL, 'packs/rp.zip')
        downloader.download_file(BP_URL, 'packs/bp.zip')
        print('Downloaded!')

        if os.path.exists('packs/rp'):
            shutil.rmtree('packs/rp')

        print('Extracting resource pack...')
        with ZipFile('packs/rp.zip') as unzipping_file:
            unzipping_file.extractall('packs/rp')
        print('Extracted!')

        if os.path.exists('packs/bp'):
            shutil.rmtree('packs/bp')

        print('Extracting behavior pack...')
        with ZipFile('packs/bp.zip') as unzipping_file:
            unzipping_file.extractall('packs/bp')
        print('Extracted!')

    # Extract custom data
    for element in os.listdir('custom_data/'):
        if not element.endswith('.zip'):
            shutil.rmtree('custom_data/'+element)
        else:
            with ZipFile('custom_data/'+element) as unzipping_file:
                unzipping_file.extractall('custom_data/'+element.replace('.zip', ''))

    # Wiki repo folder local path
    if os.path.exists('wiki_local_path.txt'):
        wiki_path_file = open('wiki_local_path.txt', 'r+')
        wiki_path = wiki_path_file.read()
        if wiki_path == '':
            print('Select Wiki repository folder')
            wiki_path = filedialog.askdirectory()
            wiki_path_file.write(wiki_path)
        else:
            for line in wiki_path_file:
                wiki_path = line
                break
    else:
        print('Select Wiki repository folder')
        with open('wiki_local_path.txt', 'w') as wiki_path_file:
            wiki_path=filedialog.askdirectory()
            wiki_path_file.write(wiki_path)

    # Data generation
    is_stable = DOWNLOAD_MODE == 'stable'
    rp_path = 'packs/rp'
    bp_path = 'packs/bp'
    custom_data_path = 'custom_data'
    test_page_path = 'test-page.md'

    # Content generation
    version = wcg.get_version(rp_path, is_stable)
    wiki_tools.upload_content(wiki_path+'/docs/blocks/block-sounds.md', wcg.get_block_sounds(rp_path, version)) # block sounds
    wiki_tools.upload_content(wiki_path+'/docs/commands/nbt-commands.md', wcg.can_place_on_everything(rp_path, version)) # can_place_on_everything
    wiki_tools.upload_content(wiki_path+'/docs/documentation/creative-categories.md', wcg.get_creative_categories_table(rp_path, version)) # creative categories
    wiki_tools.upload_content(wiki_path+'/docs/documentation/fog-ids.md', wcg.get_fogs_table(rp_path, version)) # fog ids
    wcg.generate_sound_definitions(rp_path, version, wiki_path+'/docs/documentation/sound-definitions.md') # sound definitions
    wcg.generate_biome_tags_tables(custom_data_path+'/biomes', version, wiki_path+'/docs/world-generation/biome-tags.md') # biome and tags tables
    wcg.generate_vu_spawn_rules(bp_path, version, wiki_path+'/docs/entities/vanilla-usage-spawn-rules.md', 8) # vanilla usage spawn rules
    wcg.generate_vu_items(bp_path, version, wiki_path+'/docs/items/vanilla-usage-items.md', 8) # vanilla usage items
    wcg.generate_vu_entities(bp_path, version, wiki_path+'/docs/entities/vanilla-usage-components.md', 8, 3) # vanilla usage entities


if __name__ == "__main__":
    main()

print('Finished!')