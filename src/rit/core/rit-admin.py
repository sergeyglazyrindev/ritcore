#!/home/sergeyg/.virtualenvs/rit/bin/python
# EASY-INSTALL-DEV-SCRIPT: 'rit.core==0.1','rit-admin.py'
import os

os.environ['RIT_SETTINGS_MODULE'] = 'dummy_settings'
__requires__ = 'rit.core==0.1'
__import__('pkg_resources').require('rit.core==0.1')
__file__ = '/home/sergeyg/Projects/Personal/ritnamespace/ritcore/bin/rit-admin.py'
exec(compile(open(__file__).read(), __file__, 'exec'))
