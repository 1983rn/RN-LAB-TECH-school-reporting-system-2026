import os
import sys
import traceback

out = os.path.join(os.path.dirname(__file__), 'numpy_diag.txt')
with open(out, 'w', encoding='utf-8') as f:
    f.write(f"cwd: {os.getcwd()}\n")
    f.write(f"sys.executable: {sys.executable}\n")
    f.write(f"sys.path[0]: {sys.path[0]!r}\n")
    f.write('sys.path:\n')
    for p in sys.path:
        f.write(f"  {p}\n")
    f.write(f"\nPYTHONPATH: {os.environ.get('PYTHONPATH')}\n")

    p = os.getcwd()
    f.write('\nListing directories from cwd upward for names starting with "numpy":\n')
    while True:
        f.write(f"Inspecting {p}\n")
        try:
            for name in os.listdir(p):
                if name.lower().startswith('numpy'):
                    f.write(f"  FOUND: {name}\n")
        except Exception as e:
            f.write(f"  error listing: {e}\n")
        parent = os.path.dirname(p)
        if parent == p:
            break
        p = parent

    f.write('\nAttempting import numpy:\n')
    try:
        import numpy
        f.write(f"Imported numpy from: {getattr(numpy, '__file__', None)}\n")
    except Exception:
        f.write(traceback.format_exc())

print('wrote', out)
