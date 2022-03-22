'''DO NOT TOUCH!!!'''
activate_this = '/home/ubuntu/flaskproject/venv/bin/activate_this.py'
with open(activate_this) as f:
	exec(f.read(), dict(__file__=activate_this))

import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/html/flaskproject/venv/")

from MyApp import app as application
'''DO NOT TOUCH!!!'''