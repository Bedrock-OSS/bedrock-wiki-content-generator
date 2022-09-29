def upload_content(page_path: str, *args):
    """Uploads content to page. Takes page path and content list(s)."""

    start_flag_name = '<!-- page_dumper_start -->'
    end_flag_name = '<!-- page_dumper_end -->'

    with open(page_path, encoding='UTF-8') as wiki_page:
        lined_wiki_page = list(wiki_page)
    dumping_content = args

    dumper_start_counter = 0
    dumper_end_counter = 0

    for line in lined_wiki_page:
        if start_flag_name in line:
            dumper_start_counter += 1
        elif end_flag_name in line:
            dumper_end_counter += 1

    if dumper_start_counter != dumper_end_counter:
        print(f'Error! {page_path} is missing one or more start/end flag!')
        exit()
    dumper_flag_counter = dumper_start_counter
    if dumper_flag_counter != len(dumping_content):
        print(f'Error! {page_path}: Flag pairs and content amount must match!')
        exit()

    start_flag_index = 0
    updating_wiki_page = []
    uncleared_content_count = dumper_flag_counter
    loop_count = 1
    while uncleared_content_count > 0:
        for line_index in range(len(lined_wiki_page)):
            if start_flag_name in lined_wiki_page[line_index]:
                start_flag_index = line_index
            if start_flag_index != 0:
                is_content_cleared = False
                while not is_content_cleared:
                    for content_line_index in range(start_flag_index+1, len(lined_wiki_page)+1):
                        if end_flag_name in lined_wiki_page[content_line_index]:
                            is_content_cleared = True
                            uncleared_content_count -= 1
                            break
                        else:
                            lined_wiki_page.pop(content_line_index)
                            break
                break
        if loop_count == 1 and uncleared_content_count == 0:
            # Include flags as it is the last loop
            updating_wiki_page = lined_wiki_page[:start_flag_index+2]
            lined_wiki_page = lined_wiki_page[start_flag_index+2:]
        if uncleared_content_count != 0:
            # Avoid flags duplication
            updating_wiki_page += lined_wiki_page[:start_flag_index]
            lined_wiki_page = lined_wiki_page[start_flag_index:]
        else:
            updating_wiki_page += lined_wiki_page[:start_flag_index+2]
            lined_wiki_page = lined_wiki_page[start_flag_index+2:]
        loop_count += 1
    updating_wiki_page += lined_wiki_page # [2:]

    start_flag_positions = []
    for line_index in range(len(updating_wiki_page)):
        if start_flag_name in updating_wiki_page[line_index]:
            start_flag_positions.append(line_index)

    for content in dumping_content[::-1]:
        if type(content) == list:
            content = [line + '\n' for line in content]
        else:
            content = list(content+'\n')
        updating_wiki_page = updating_wiki_page[:start_flag_positions[-1]+1] + content + updating_wiki_page[start_flag_positions[-1]+1:]
        start_flag_positions.pop(-1)

    with open(page_path, 'w', encoding='UTF-8') as wiki_page:
        for line in updating_wiki_page:
            wiki_page.write(line)

    print(page_path[page_path.rfind('/')+1:]+' - successfully uploaded!')

def table(sort_column_index: int, *args: list):
    """Creates a table from given lists (one list - one column). If you don't want your table to be sorted, set sort_column_index to -1."""
    columns = args
    generated_table = []

    column_lines_max_len = []
    for content_column in columns:
        column_lines_max_len.append(len(max(content_column, key=len)))

    # Add empty lines to columns
    column_lines_count = []
    for column_index in range(len(columns)):
        column_lines_count.append(len(columns[column_index]))
    if max(column_lines_count) != min(column_lines_count):
        for column_index in range(len(columns)):
            for _ in range(max(column_lines_count)-len(columns[column_index])):
                columns[column_index].append('')
    
    # Sort lines in columns
    if sort_column_index != -1:
        headers = []
        for column_index in range(len(columns)):
            headers.append(columns[column_index][0])
            columns[column_index].pop(0)
        sorted_line_indexes = []
        for sorted_line in sorted(columns[sort_column_index]):
            sorted_line_indexes.append(columns[sort_column_index].index(sorted_line))
        sorted_columns = {}
        for i in range(len(columns)):
            sorted_columns[i] = []
        for column_index in range(len(columns)):
            for sorted_line_index in sorted_line_indexes:
                sorted_columns[column_index].append(columns[column_index][sorted_line_index])
        columns = []
        for column_list in sorted_columns.values():
            columns.append(column_list)
        for column_index in range(len(columns)):
            columns[column_index].insert(0, headers[column_index])

    # Generate table lines
    for content_line_index in range(len(columns[0])):
        table_line = '| '
        for column_index in range(len(columns)):
            content_line = columns[column_index][content_line_index]
            namespace_count = column_lines_max_len[column_index] - len(content_line)
            table_line += content_line + ' '*namespace_count + ' |' + ' '*bool(len(columns)-1)
        generated_table.append(table_line)

    # Generate and add an after header line
    after_header_line = '| '
    for column_index in range(len(columns)):
        after_header_line += '-'*(column_lines_max_len[column_index]) + ' |' + ' '*bool(len(columns)-1)
    generated_table.insert(1, after_header_line)

    return generated_table