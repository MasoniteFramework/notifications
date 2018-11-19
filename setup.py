from setuptools import setup

setup(
    name='masonite-notifications',
    packages=[
        'notifications',
        'notifications.components',
        'notifications.snippets',
        'notifications.providers',
        'notifications.commands',
    ],
    version='0.0.5',
    install_requires=[],
    description='The core for the Masonite framework',
    author='Joseph Mancuso',
    author_email='idmann509@gmail.com',
    url='https://github.com/MasoniteFramework/notifications',
    keywords=['python web framework', 'python3', 'masonite'],
    classifiers=[],
    include_package_data=True,
)
