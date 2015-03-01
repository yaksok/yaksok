import glob
import subprocess

for file_path in glob.glob('codes/*.yak'):
    print(file_path, '...', end=' ')
    target = open(file_path + '.out', 'rb').read()
    output = subprocess.check_output(
        ['python3', 'yaksok/yaksok.py', file_path])
    if output == target:
        print('success!')
    else:
        print('failed!')
