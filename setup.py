from distutils.core import setup

setup(
    name='pykintone',
    packages=['pykintone'],
    install_requires=[
        'PyYAML',
        'requests'
    ],
    version='0.0.1',
    description='Python library to access kintone',
    author='icoxfog417',
    author_email='icoxfog417@yahoo.co.jp',
    url='https://github.com/icoxfog417/pykintone',
    download_url='https://github.com/icoxfog417/pykintone/tarball/master',
    keywords=['kintone'],
    classifiers=[],
)
