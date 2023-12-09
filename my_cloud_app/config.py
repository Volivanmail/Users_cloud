from jproperties import Properties

config = Properties()

with open('my_cloud_app/app_config.properties', 'rb') as config_file:
    config.load(config_file)

DB_ENGINE = config.get('DB_ENGINE').data
DB_NAME = config.get('DB_NAME').data
DB_USER = config.get('DB_USER').data
DB_PASSWORD = config.get('DB_PASSWORD').data
DB_HOST = config.get('DB_HOST').data
DB_PORT = config.get('DB_PORT').data
BASE_DIR_STORAGE = config.get('BASE_DIR_STORAGE').data