# Bedrock Wiki Content Generator

Documentation scraper for the Minecraft Bedrock Edition [wiki](https://wiki.bedrock.dev/).
Rewrite of the [Bedrock Harvester](https://github.com/Bedrock-OSS/bedrock-harvester).
This tool can be run on Minecraft base-game files, including the hosted Vanilla Packs files, or those pulled from the `.apk`.
Feel free to contribute, ask for new content generation or existing one update.
Maintained by [Bedrock OSS](https://discord.gg/XjV87YN) organization, mostly by MJ105#0448.

# Setup

1. Clone repo
2. `cd ./..`
3. `pip install -r requirements.txt`

# Running

1. `cd ./..`
2. `python main.py` (+ args)
3. Provide data program asks for.

*You might need to uncomment some functions in # Content generation*

# Running Options

Default configuration (no arguments) downloads the stable version of packs.
If you want to change configuration, add:

```
--skip_download
--download_mode ["stable" or "beta"]
--rp_url <the url to download resourcepack>
--bp_url <the url to download behaviorpack>
```

`--skip_download` also removes pack extraction.

Examples:
- Download beta packs and extract data from them:
    `python main.py --download_mode beta`

- Downloading packs from custom urls:
    `python main --bp_url example1.com --rp_url example2.com`

# Data

The scripts uses temporary path `packs`, where vrp and vbp are downloaded. The path is not cleared after the execution, it conditionally removed and added again at the start of the script.

You can add custom data (that is not in vanilla packs) to `custom_data` folder. Make sure it is zipped.

**Note**:
Last updated for version is based on min_engine_version in manifest.json, which is not always changed. Like if packs version is 1.18.31, it will still say "1.18.30".

# FAQ

**Q**: Where can I see everything what this script changes/generates?

**A**: You can find what content this script generates in content_list.txt file.

**Q**: I changed local path of wiki repo, how can I fix script's target folder?

**A**: Delete wiki_local_path.txt file or clear it and run the script again.

**Q**: Why 'Last updated for version' doesn't match example packs version?

**A**: There aren't any actual version markers in vanilla packs, so `min_engine_version` is used. If something new (like entity, block or important fix) is added, this version gets changes.

**Q**: I want to contribute to this project, where should I go?

**A**: View CONTRIBUTING.md.
