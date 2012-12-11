from settings_common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

import dj_database_url
DATABASES = {}
DATABASES['default'] = dj_database_url.config()
