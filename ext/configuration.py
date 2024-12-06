import os

URL = os.environ.get('URL')
URL_OS = os.environ.get('URL_OS')
HEADERS = {'Content-Type': 'application/json',
           'access-token': os.environ.get('ACCESS_TOKEN'),
           'secret-access-token': os.environ.get('SECRET_ACCESS_TOKEN')}


# Fetch environment variables to configure the application settings
def init_app(app):
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['PERMANENT_SESSION_LIFETIME'] = int(os.environ.get('PERMANENT_SESSION_LIFETIME'))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('MYSQL_URL')
