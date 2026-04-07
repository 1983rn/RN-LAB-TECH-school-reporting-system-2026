import traceback
import sys
import os
out = os.path.join(os.path.dirname(__file__), 'trace_imports.txt')
with open(out, 'w', encoding='utf-8') as f:
    f.write('sys.executable: ' + sys.executable + '\n')
    f.write('cwd: ' + os.getcwd() + '\n')
    f.write('PYTHONPATH: ' + repr(os.environ.get('PYTHONPATH')) + '\n')
    f.write('\n--- Trying import pandas ---\n')
    try:
        import pandas
        f.write('pandas imported OK from: ' + repr(getattr(pandas, '__file__', None)) + '\n')
    except Exception:
        f.write(traceback.format_exc() + '\n')

    f.write('\n--- Trying import app (project) ---\n')
    # Ensure repo root is on sys.path
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    try:
        import app
        f.write('app imported OK\n')
    except Exception:
        f.write(traceback.format_exc() + '\n')

print('wrote', out)
