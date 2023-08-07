import os

bind = '0.0.0.0'
port = int(os.environ.get('PORT', '8000'))

workers = 4