import subprocess
import sys

print('Listing python processes...')
res = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'], capture_output=True, text=True)
print(res.stdout)
if 'python.exe' in res.stdout:
    print('Killing python.exe processes...')
    subprocess.run(['taskkill', '/F', '/IM', 'python.exe'])
    print('Kill command executed')
else:
    print('No python.exe processes found')
