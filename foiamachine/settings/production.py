from common import *


STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
DEFAULT_S3_PATH = "media"
STATIC_S3_PATH = "static"
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', "")
USE_S3 =  True


DOCUMENTCLOUD_USERNAME=env("DOCUMENTCLOUD_USERNAME","")
DOCUMENTCLOUD_PASS=env("DOCUMENTCLOUD_PASS", "")

DEBUG = bool(env('DEBUG', ''))
MG_ROUTE = env('MG_ROUTE', '')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'foiamachine',
        'PORT': '3306', # PgBouncer port
        'HOST': env("DBHOST", ""),
        'USER': env("DBUSER", ""),
        'PASSWORD': env("DBPASS", "")
    }
}

if env("MYSQL_SSL_PATH", "") != "":
    DATABASES['default']['OPTIONS'] = {'ssl': {'ca': env("MYSQL_SSL_PATH", "")}}

MEDIA_URL = env("MEDIA_URL", "")
STATIC_URL = env("STATIC_URL", "")
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True
    SSL_PREPEND_WWW = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

VET_REGISTRATION = False 
#COMPRESS_URL = STATIC_URL
#COMPRESS_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
COMPRESS_ENABLED = False 
COMPRESS_OFFLINE = True
# Caching
CACHE_MIDDLEWARE_SECONDS = 90 * 60 # 90 minutes

os.environ['MEMCACHE_SERVERS'] = os.environ.get('MEMCACHIER_SERVERS', '').replace(',', ';')
os.environ['MEMCACHE_USERNAME'] = os.environ.get('MEMCACHIER_USERNAME', '')
os.environ['MEMCACHE_PASSWORD'] = os.environ.get('MEMCACHIER_PASSWORD', '')
CACHES = {
  'default': {
    'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
    'TIMEOUT': 1000,
    'BINARY': True,
    'OPTIONS': {
        'tcp_nodelay': True,
        'remove_failed': 4
    }
  }
}



