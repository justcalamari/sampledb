from setuptools import setup, find_packages

setup(
    name='sampledb',
    version='0.1.1',
    packages=find_packages(),
    package_data={'sampledb': ['*.xsh', 'data/*.json']},
    scripts=['scripts/publish_samples', 'scripts/download_samples'],
    description='database search and publish',
    zip_safe=False,
)
# WARNING!!! Do not use setuptools 'console_scripts'
# It validates the depenendcies everytime the 'publish_samples' and
# 'download_samples' commands are run. This validation adds ~0.2 sec. to 
# the startup time of xonsh - for every single xonsh run. So never ever
# write the following:
#
#     'console_scripts': [
#         'publish_samples=sampledb.reader:publish_samples',
#         'download_samples=sampledb.reader:download_samples',
#     ],
#
# END WARNING
