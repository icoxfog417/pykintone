from distutils.core import setup

setup(
    name='pykintone',
    packages=['pykintone', 'pykintone.application_settings'],
    install_requires=[
        'PyYAML',
        'requests'
    ],
    version='0.2.0',
    description='Python library to access kintone',
    author='icoxfog417',
    author_email='icoxfog417@yahoo.co.jp',
    url='https://github.com/icoxfog417/pykintone',
    download_url='https://github.com/icoxfog417/pykintone/tarball/0.2.0',
    keywords=['kintone'],
    classifiers=[],
)
