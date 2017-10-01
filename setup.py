import ast
from setuptools import setup, find_packages


def find_version(filename):
    with open(filename) as f:
        initlines = f.readlines()
    version_line = None
    for line in initlines:
        if line.startswith('__version__'):
            vstr = line.strip().split()[-1]
            ver = ast.literal_eval(vstr)
            break
    return ver

setup(
    name='sampledb',
    version=find_version('sampledb/__init__.py'),
    packages=find_packages(),
    description='database search and publish',
    zip_safe=False,
)

