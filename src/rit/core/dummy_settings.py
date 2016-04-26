import os

PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
))

TEMPLATE_FOLDERS = tuple([
    os.path.join(PROJECT_ROOT, "templates"),
])

import local_settings

locals().update({setting: getattr(local_settings, setting)
                 for setting in dir(local_settings) if not setting.startswith('_')})
