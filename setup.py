import sys

# Downloads setuptools if not find it before try to import
try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass

from setuptools import setup

packages = ['googletracks']

install_requires = ['httplib2','oauth2client']
if sys.version_info[0] <= 2 and sys.version_info[1] <= 5:
    install_requires.append('simplejson')

setup(
    name='Google Tracks API Wrapper',
    version=0.1,
    #url='',
    author="Marinho Brandao",
    license="BSD License",
    packages=packages,
    install_requires=install_requires,
    )
