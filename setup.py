from setuptools import setup, find_packages


PACKAGE_NAME = 'psc'
VERSION = open('version').readline()

setup(
    name=PACKAGE_NAME,
    url="https://git.anvileight.com/alexey.voloshin/psc.git",
    maintainer="Alexey Voloshin",
    maintainer_email="alexey.voloshin@anvileight.com",
    version=VERSION,
    description="PSC project",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['**/*.html', '**/static/*.*'],
    },
)