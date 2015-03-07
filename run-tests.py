import glob
import os
import subprocess
import traceback


patterns = [
    'yaksok/tests/codes/*.yak',
    'yaksok/tests/codes/*/*.yak',
]

for file_path in sum((glob.glob(_) for _ in patterns), []):
    print(file_path, '...', end=' ')
    target_file_path = file_path + '.out'
    if not os.path.exists(target_file_path):
        print('no .out file!')
        continue
    target = open(target_file_path, 'rb').read()
    proc = subprocess.Popen(
        ['python3', '-m', 'yaksok', file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    output = proc.stdout.read()
    error = proc.stderr.read()
    proc.communicate()
    if error or proc.returncode:
        print('error! (status code {})'.format(proc.returncode))
        print(error.decode('utf8', 'ignore'))
        print('=' * 32)
        continue
    if output == target:
        print('success!')
    else:
        print('failed!')
