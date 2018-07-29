from setuptools import setup
from masonite.info import VERSION

setup(
    name='masonite',
    packages=[
        'notifications',
        'notifications.components',
        'notifications.snippets',
    ],
    version='0.0.1',
    install_requires=[],
    description='The core for the Masonite framework',
    author='Joseph Mancuso',
    author_email='idmann509@gmail.com',
    url='https://github.com/MasoniteFramework/notifications',
    keywords=['python web framework', 'python3', 'masonite'],
    classifiers=[],
    include_package_data=True,
)
