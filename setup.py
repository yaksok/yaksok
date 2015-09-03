from setuptools import setup

setup(
    name='yaksok',
    packages=['yaksok', 'yaksok.ply', 'yaksok.modules'],
    package_data = {
        '':[ 'modules/*.yak'],
    },
    entry_points = {
        'console_scripts': [
            'yaksok = yaksok.yaksok:main',
        ],
    },
)
