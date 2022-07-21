import json
import jsonc_decoder
import wiki_tools
import os


def get_version(rp_path: str, is_stable: bool):
    """Gets `min_engine_version` (which is used as version) from vrp."""
    with open(rp_path+'/manifest.json') as manifest:
        manifest_data = json.load(manifest)
    version = f'*Last updated for {".".join(map(str, manifest_data["header"]["min_engine_version"]))}*'
    if not is_stable:
        version = version[::-1] + ' (beta)*'
    return version

def get_block_sounds(rp_path: str, version: str):
    """Generates list with all possible values for 'sound' in blocks.json. Used in https://wiki.bedrock.dev/blocks/block-sounds.html"""
    block_sounds = []
    invalid_values = []
    with open(rp_path+'/blocks.json', 'r') as blocks_json:
        blocks_json_data = json.load(blocks_json)
    for value in blocks_json_data.values():
        if 'sound' in value:
            block_sounds.append(value['sound'])
    block_sounds = sorted(list(set(block_sounds)))
    for excluding_sound in invalid_values:
        block_sounds.remove(excluding_sound)
    page_content = '```json\n' + json.dumps(block_sounds, indent=4) + '\n```' + '\n'+ version
    return page_content

def can_place_on_everything(rp_path: str, version: str):
    """Generates a commands wrapped in codeheader for https://wiki.bedrock.dev/commands/nbt-commands.html#canplaceon-everything"""
    blocks_list = []
    invalid_values = ['format_version']
    with open(rp_path+'/'+'blocks.json', 'r') as blocks_json:
        blocks_json_data = json.load(blocks_json)
        for block in blocks_json_data:
            blocks_list.append(block)
    for excluding_element in invalid_values:
        blocks_list.remove(excluding_element)
    nbt_component = {
        "minecraft:can_place_on": {}
    }
    nbt_component['minecraft:can_place_on']['blocks'] = blocks_list
    can_place_on_everything_command = 'give @p stone 1 0 ' + json.dumps(nbt_component)
    can_place_on_everything_command = '<CodeHeader></CodeHeader>\n\n```json\n' + can_place_on_everything_command + '\n```' + '\n\n'+ version
    return can_place_on_everything_command

def get_creative_categories_table(rp_path: str, version: str):
    """Generates table for https://wiki.bedrock.dev/documentation/creative-categories.html#list-of-creative-categories"""
    lines_with_categories = []
    categories = []
    with open(rp_path+'/texts/en_US.lang', 'r') as lang_file:
        for line in lang_file:
            if "itemGroup.name." in line:
                lines_with_categories.append(line)
    for line in lines_with_categories:
        categories.append(line.split('=')[0])
    categories.insert(0, 'Creative Categories:')
    categories_table = wiki_tools.table(0, categories)
    categories_table.append('')
    categories_table.append(version)
    return categories_table

def get_fogs_table(rp_path: str, version: str):
    """Generates table for https://wiki.bedrock.dev/documentation/fog-ids.html#auto-generated"""
    fogs_table = []
    biome_names = []
    fog_ids = []
    with open(rp_path+'/biomes_client.json', 'r') as biomes_client:
        biomes_client_data = json.load(biomes_client)
    for biome_name, biome_data in biomes_client_data['biomes'].items():
        biome_names.append(biome_name)
        fog_ids.append(biome_data['fog_identifier'])
    fog_ids.insert(0, 'ID')
    biome_names.insert(0, 'Biome used in')
    fogs_table = wiki_tools.table(0, fog_ids, biome_names)
    fogs_table.append(version)
    return fogs_table

def generate_sound_definitions(rp_path: str, version: str, wiki_page_path: str):
    """Generates and writes data for https://wiki.bedrock.dev/documentation/sound-definitions.html"""
    with open(rp_path+'/sounds/sound_definitions.json', 'r') as sound_definitions:
        default_sound_definitions_data = json.load(sound_definitions)
    sound_categories = []
    for sound_data in default_sound_definitions_data['sound_definitions'].values():
        try:
            sound_categories.append(sound_data['category'])
        except:
            pass
    sound_categories = sorted(set(sound_categories))
    sound_categories.append('No category')
    sound_definitions_data = {}
    for category_name in sound_categories:
        sound_definitions_data[category_name] = []
    for sound_name, sound_data in default_sound_definitions_data['sound_definitions'].items():
        try:
            sound_definitions_data[sound_data['category']].append(sound_name)
        except:
            sound_definitions_data['No category'].append(sound_name)
    wiki_page =  open(wiki_page_path, 'w')
    wiki_page.write('---\n')
    wiki_page.write('title: Sound Definitions\n')
    wiki_page.write('mentions:\n')
    wiki_page.write('    - MedicalJewel105\n')
    wiki_page.write('---\n\n')
    wiki_page.write('Sounds from `sound_definitions.json` sorted by categories and subcategories based on their names.\n')
    wiki_page.write(f'This page was created with [Wiki Content Generator](https://github.com/Bedrock-OSS/bedrock-wiki-content-generator). If there are issues, contact us on [Bedrock OSS](https://discord.gg/XjV87YN) Discord server.\n{version}\n\n')
    for sound_category, sound_list in sound_definitions_data.items():
        wiki_page.write(f'## {sound_category}\n\n')
        previous_subcategory = ''
        current_subcategory = ''
        for sound_name in sorted(sound_list):
            if '.' in sound_name:
                current_subcategory = sound_name.split('.')[0]
                if previous_subcategory != current_subcategory:
                    wiki_page.write(f'#### {current_subcategory}\n---\n')
                    wiki_page.write(f'`{sound_name}`\n\n')
                    previous_subcategory = current_subcategory
                else:
                    wiki_page.write(f'`{sound_name}`\n\n')
            else:
                wiki_page.write(f'`{sound_name}`\n\n')
    print('Updated sound definitions!')

def generate_biome_tags_tables(biomes_folder_path: str, version: str, wiki_page_path: str):
    """Generates and writes tables for https://wiki.bedrock.dev/world-generation/biome-tags.html"""
    all_biome_data = {}
    table_1_biome_id = ['Biome']
    table_1_biome_tags = ['Biome Tags']
    table_2_biome_tags = ['Biome Tag']
    table_2_biomes = ['Biomes']
    all_biome_tags = []
    for biome_filename in os.listdir(biomes_folder_path):
        all_biome_data[biome_filename.replace('.biome.json', '')] = []
        with open(biomes_folder_path+'/'+biome_filename) as biome_file:
            biome_data = json.load(biome_file, cls=jsonc_decoder.JSONCDecoder)
        biome_id = biome_data['minecraft:biome']['description']['identifier']
        table_1_biome_id.append(biome_id)
        biome_tags = ', '
        for biome_component_name in biome_data['minecraft:biome']['components']:
            if ':' not in biome_component_name and biome_data['minecraft:biome']['components'][biome_component_name] == {}:
                biome_tags += biome_component_name + ', '
                all_biome_tags.append(biome_component_name)
                all_biome_data[biome_filename.replace('.biome.json', '')].append(biome_component_name)
        table_1_biome_tags.append(biome_tags.strip(', '))
    biome_tag_per_biome = wiki_tools.table(0, table_1_biome_id, table_1_biome_tags)
    all_biome_tags = sorted(set(all_biome_tags))
    for biome_tag in all_biome_tags:
        table_2_biome_tags.append(biome_tag)
        matching_biomes = ', '
        for biome_name, biome_tags_list in all_biome_data.items():
            if biome_tag in biome_tags_list:
                matching_biomes += biome_name + ', '
        table_2_biomes.append(matching_biomes.strip(', '))
    biome_per_biome_tag = wiki_tools.table(0, table_2_biome_tags, table_2_biomes)
    wiki_page = open(wiki_page_path, 'w')
    wiki_page.write('---\n')
    wiki_page.write('title: Biome Tags\n')
    wiki_page.write('category: Documentation\n')
    wiki_page.write('mentions:\n')
    wiki_page.write('    - MedicalJewel105\n')
    wiki_page.write('---\n\n')
    wiki_page.write('This page was created with [Wiki Content Generator](https://github.com/Bedrock-OSS/bedrock-wiki-content-generator). If there are issues, contact us on [Bedrock OSS](https://discord.gg/XjV87YN) Discord server.\n')
    wiki_page.write(f' {version}\n\n')
    wiki_page.write('## Biome tag per Biome\n\n')
    for line in biome_tag_per_biome:
        wiki_page.write(line+'\n')
    wiki_page.write('\n## Biome per Biome Tag\n\n')
    for line in biome_per_biome_tag:
        wiki_page.write(line+'\n')
    print('Updated biome tags!')

def generate_vu_spawn_rules(bp_path: str, version: str, wiki_page_path: str, example_amount: int):
    """Generates and writes vanilla usage spawn rules: https://wiki.bedrock.dev/entities/vanilla-usage-spawn-rules.html or https://wiki.bedrock.dev/entities/vusr-full.html. To bypass the example limit, set it to -1."""
    components_data = {}
    # In generate_ functions data is stored in the following or similar way:
    # components_data = {
    #   "component_name": [
    #       {
    #           "source": "",
    #           "component":{<component_data>}
    #       }
    #   ]
    # }
    for spawn_rules_filename in os.listdir(bp_path+'/spawn_rules/'):
        with open(bp_path+'/spawn_rules/'+spawn_rules_filename) as spawn_rules_file:
            spawn_rules_data = json.load(spawn_rules_file, cls=jsonc_decoder.JSONCDecoder)
        for condition in spawn_rules_data.get('minecraft:spawn_rules', {}).get('conditions', {}):
            for component_name, component_data in condition.items():
                if component_name not in components_data:
                    components_data[component_name] = []
                component_usage = {}
                component_usage['entity'] = spawn_rules_data['minecraft:spawn_rules']['description']['identifier'].split('minecraft:')[1]
                component_usage[component_name] = component_data
                components_data[component_name].append(component_usage)
    wiki_page = open(wiki_page_path, 'w')
    wiki_page.write('---\n')
    wiki_page.write('title: Vanilla Usage Spawn Rules\n')
    wiki_page.write('category: Documentation\n')
    wiki_page.write('mentions:\n')
    wiki_page.write('    - MedicalJewel105\n')
    wiki_page.write('---\n\n')
    wiki_page.write('This page was created with [Wiki Content Generator](https://github.com/Bedrock-OSS/bedrock-wiki-content-generator). If there are issues, contact us on [Bedrock OSS](https://discord.gg/XjV87YN) Discord server.\n')
    if example_amount == -1:
        wiki_page.write(f'Includes all examples. Namespace `minecraft` was also removed.')
    else:
        wiki_page.write(f'Note that not more than {example_amount} examples are shown for each component to keep this page fast to load. Namespace `minecraft` was also removed.')
        wiki_page.write('If you want to see full page, you can do it [here](/entities/vusr-full).') # not affected through main.py
    wiki_page.write(f' {version}\n\n')
    for component_name in sorted(components_data):
        wiki_page.write('## '+component_name.replace('minecraft:', '')+'\n\n')
        wiki_page.write('<Spoiler title="Show">\n\n')
        component_usage_counter = 0
        current_entity = ''
        for example in components_data[component_name]:
            if current_entity != example['entity']:
                current_entity = example['entity']
                wiki_page.write(example['entity'].replace('minecraft:', '')+'\n\n')
            wiki_page.write('<CodeHeader></CodeHeader>\n\n')
            wiki_page.write('```json\n')
            wiki_page.write(f'"{component_name}": '+json.dumps(example[component_name], indent=4)+'\n')
            wiki_page.write('```\n\n')
            component_usage_counter += 1
            if component_usage_counter == example_amount:
                break
        wiki_page.write('</Spoiler>\n\n')
    print('Updated Vanilla Usage Spawn Rules!')

def generate_vu_items(bp_path: str, version: str, wiki_page_path: str, example_amount: int):
    """Generates and writes vanilla usage item components: https://wiki.bedrock.dev/items/vanilla-usage-items.html or https://wiki.bedrock.dev/items/vui-full.html. To bypass the example limit, set it to -1."""
    components_data = {}
    for item_filename in os.listdir(bp_path+'/items/'):
        with open(bp_path+'/items/'+item_filename) as item_file:
            item_data = json.load(item_file, cls=jsonc_decoder.JSONCDecoder)
        for component_name, component_data in item_data['minecraft:item'].get('components', {}).items():
            if component_name not in components_data:
                components_data[component_name] = []
            component_usage = {}
            component_usage['item'] = item_data['minecraft:item']['description']['identifier']
            component_usage[component_name] = component_data
            components_data[component_name].append(component_usage)
    wiki_page = open(wiki_page_path, 'w')
    wiki_page.write('---\n')
    wiki_page.write('title: Vanilla Usage Components\n')
    wiki_page.write('category: Documentation\n')
    wiki_page.write('mentions:\n')
    wiki_page.write('    - MedicalJewel105\n')
    wiki_page.write('---\n\n')
    wiki_page.write('This page was created with [Wiki Content Generator](https://github.com/Bedrock-OSS/bedrock-wiki-content-generator). If there are issues, contact us on [Bedrock OSS](https://discord.gg/XjV87YN) Discord server.\n')
    if example_amount == -1:
        wiki_page.write(f'Includes all examples. Namespace `minecraft` was removed.')
    else:
        wiki_page.write(f'Note that not more than {example_amount} examples are shown for each component to keep this page fast to load. Namespace `minecraft` was also removed.\n')
        wiki_page.write('If you want to see full page, you can do it [here](/items/vui-full).') # not affected through main.py
    wiki_page.write(f' {version}\n\n')
    for component_name in sorted(components_data):
        wiki_page.write('## '+component_name.replace('minecraft:', '')+'\n\n')
        wiki_page.write('<Spoiler title="Show">\n\n')
        component_usage_counter = 0
        current_item = ''
        for example in components_data[component_name]:
            if current_item != example['item']:
                current_item = example['item']
                wiki_page.write(example['item'].replace('minecraft:', '')+'\n\n')
            wiki_page.write('<CodeHeader></CodeHeader>\n\n')
            wiki_page.write('```json\n')
            wiki_page.write(f'"{component_name}": '+json.dumps(example[component_name], indent=4)+'\n')
            wiki_page.write('```\n\n')
            component_usage_counter += 1
            if component_usage_counter == example_amount:
                break
        wiki_page.write('</Spoiler>\n\n')
    print('Updated Vanilla Usage Items!')

def generate_vu_entities(bp_path: str, version: str, wiki_page_path: str, example_amount: int, entity_example_amount: int):
    """Generates and writes vanilla usage components: https://wiki.bedrock.dev/entities/vanilla-usage-components.html.
    Example amount is max amount of examples for component from different entities, entity example amount - max amount of examples from entity. Use -1 to bypass."""
    components_data = {}
    for item_filename in os.listdir(bp_path+'/entities/'):
        with open(bp_path+'/entities/'+item_filename) as entity_file:
            entity_data = json.load(entity_file, cls=jsonc_decoder.JSONCDecoder)
        for component_name, component_data in entity_data['minecraft:entity']['components'].items():
            if component_name not in components_data:
                components_data[component_name] = []
            component_usage = {}
            try:
                component_usage['entity'] = entity_data['minecraft:entity']['description']['identifier']
            except:
                component_usage['entity'] = f'minecraft:{item_filename.replace(".json", "")}'
            component_usage[component_name] = component_data
            components_data[component_name].append(component_usage)
        if 'component_groups' in entity_data['minecraft:entity']:
            for component_group in entity_data['minecraft:entity']['component_groups']:
                for component_name, component_data in entity_data['minecraft:entity']['component_groups'][component_group].items():
                    if component_name not in components_data:
                        components_data[component_name] = []
                    component_usage = {}
                    component_usage['entity'] = entity_data['minecraft:entity']['description']['identifier']
                    component_usage['component_group'] = component_group
                    component_usage[component_name] = component_data
                    components_data[component_name].append(component_usage)
    wiki_page = open(wiki_page_path, 'w')
    wiki_page.write('---\n')
    wiki_page.write('title: Vanilla Usage Components\n')
    wiki_page.write('category: Documentation\n')
    wiki_page.write('mentions:\n')
    wiki_page.write('    - MedicalJewel105\n')
    wiki_page.write('---\n\n')
    wiki_page.write('This page was created with [Wiki Content Generator](https://github.com/Bedrock-OSS/bedrock-wiki-content-generator). If there are issues, contact us on [Bedrock OSS](https://discord.gg/XjV87YN) Discord server.\n')
    if example_amount == -1:
        wiki_page.write(f'Includes all examples. Namespace `minecraft` was removed.')
    else:
        wiki_page.write(f'Note that to keep this page fast to load and informative, there are not more than {example_amount} examples for each component and not more than {entity_example_amount} example(s) from each entity are shown. Namespace `minecraft` was also removed.\n')
        wiki_page.write('If you want to see full page, you can do it [here](/entities/vuc-full).') # not affected through main.py
    wiki_page.write(f' {version}\n\n')
    for component_name in sorted(components_data):
        wiki_page.write('## '+component_name.replace('minecraft:', '')+'\n\n')
        wiki_page.write('<Spoiler title="Show">\n\n')
        component_usage_counter = 0
        entity_component_usage_counter = 0
        current_entity = ''
        for example in components_data[component_name]:
            if current_entity != example['entity']:
                current_entity = example['entity']
                entity_component_usage_counter = 0
                wiki_page.write(example['entity'].replace('minecraft:', '')+'\n\n')
            else:
                entity_component_usage_counter += 1
            if entity_component_usage_counter < entity_example_amount or entity_example_amount == -1:
                if 'component_group' in example:
                    wiki_page.write('<CodeHeader>'+'#component_groups/'+example['component_group']+'</CodeHeader>\n\n')
                else:
                    wiki_page.write('<CodeHeader></CodeHeader>\n\n')
                wiki_page.write('```json\n')
                wiki_page.write(f'"{component_name}": '+json.dumps(example[component_name], indent=4)+'\n')
                wiki_page.write('```\n\n')
                component_usage_counter += 1
            if component_usage_counter == example_amount:
                break
        wiki_page.write('</Spoiler>\n\n')
    print('Updated Vanilla Usage Entities!')