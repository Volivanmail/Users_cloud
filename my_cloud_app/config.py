from jproperties import Properties

config = Properties()

with open('my_cloud_app/app_config.properties', 'rb') as config_file:
    config.load(config_file)

BASE_DIR_STORAGE = config.get('BASE_DIR_STORAGE').data
LENGTH_OF_THE_DOWNLOAD_LINK = config.get('LENGTH_OF_THE_DOWNLOAD_LINK').data
