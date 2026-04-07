import traceback
import os
import sys

out_path = os.path.join(os.path.dirname(__file__), 'numpy_debug.txt')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write('cwd: ' + os.getcwd() + '\n')
    f.write('sys.path[0]: ' + repr(sys.path[0]) + '\n')
    f.write('sys.path snippet: ' + repr(sys.path[:10]) + '\n')
    try:
        import numpy
        f.write('numpy file: ' + repr(getattr(numpy, '__file__', None)) + '\n')
    except Exception:
        import traceback as _tb
        f.write(_tb.format_exc())
    f.flush()
print('wrote', out_path)
