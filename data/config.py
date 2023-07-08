import configparser

read_config = configparser.ConfigParser()
read_config.read('settings.ini')
try:
    BOT_TOKEN = read_config['settings']['token'].strip()
    DB_DB = read_config['settings']['db'].strip()
    DB_HOST = read_config['settings']['host'].strip()
    DB_USER = read_config['settings']['user'].strip()
    DB_PASS = read_config['settings']['password'].strip()
    if DB_DB and DB_HOST and DB_USER and DB_PASS and BOT_TOKEN:
        DB_PATH = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_DB}"
    else:
        raise Exception
    
except Exception as ex:
    exit('Переменные не найдены в файле "settings.ini" .')
    
    
def get_admins():
    read_admins = configparser.ConfigParser()
    read_admins.read('settings.ini')
    
    try:
        admins = read_admins['settings']['admin_id'].strip()
        admins = admins.replace(' ', '').split(',')
        admins = list(map(int, admins))
        return admins
    except:
        print('Админ(ы) не указан(ы)')