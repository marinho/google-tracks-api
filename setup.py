import sys

# Downloads setuptools if not find it before try to import
try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass

from setuptools import setup

install_requires = ['httplib2','oauth2client','pyopenssl']
if sys.version_info[0] <= 2 and sys.version_info[1] <= 5:
    install_requires.append('simplejson')

setup(
    name='google-tracks',
    version='0.1.2',
    url='https://github.com/TDispatch/google-tracks-api',
    author="Marinho Brandao",
    license="BSD License",
    install_requires=install_requires,
    py_modules=['googletracks'],
    )

