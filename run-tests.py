import glob
import os
import subprocess


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
    output = subprocess.check_output(
        ['python3', 'yaksok/yaksok.py', file_path])
    if output == target:
        print('success!')
    else:
        print('failed!')
