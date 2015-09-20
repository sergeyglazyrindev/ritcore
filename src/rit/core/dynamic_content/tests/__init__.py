from rit.app import settings

from os import path, walk
import fnmatch

from rit.core.dynamic_content import settings as dynamic_html_settings


def find_all_templates():
    folders_to_search_in = tuple([path.realpath(path.join(
        dynamic_html_settings.TEMPLATES_FOLDER,
        'basexml'
    )), ] + list(settings.TEMPLATE_FOLDERS))
    templates = []
    for folder in folders_to_search_in:
        for root, dirnames, filenames in walk(folder):
            for filename in fnmatch.filter(filenames, '*.xml'):
                templates.append(path.join(root, filename))
    return templates
