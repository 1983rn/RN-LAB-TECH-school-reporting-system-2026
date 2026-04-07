import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.insert(0, project_dir)

from app_minimal import app

os.environ['ENABLE_TEMPLATE_DEBUG'] = '1'

def run_template_check():
    with app.test_client() as client:
        resp = client.get('/_debug/template-check')
        print('Status code:', resp.status_code)
        print('Response data:', resp.get_data(as_text=True))
        return resp.status_code == 200

if __name__ == '__main__':
    success = run_template_check()
    sys.exit(0 if success else 1)
