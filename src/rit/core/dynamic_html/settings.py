from os import path


cur_file_path = path.dirname(__file__)
TEMPLATES_FOLDER = path.realpath(path.join(cur_file_path, '../templates/dynamic_content'))
