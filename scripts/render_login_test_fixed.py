import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.insert(0, project_dir)

# Test rendering with app_fixed
from app_fixed import app

with app.test_request_context('/'):
    tpl = app.jinja_env.get_template('login.html')
    tpl.render()

print('Full render succeeded for app_fixed')
