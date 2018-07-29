from setuptools import setup

setup(
    name='masonite-notifications',
    packages=[
        'notifications',
        'notifications.components',
        'notifications.snippets',
    ],
    version='0.0.2',
    install_requires=[],
    description='The core for the Masonite framework',
    author='Joseph Mancuso',
    author_email='idmann509@gmail.com',
    url='https://github.com/MasoniteFramework/notifications',
    keywords=['python web framework', 'python3', 'masonite'],
    classifiers=[],
    include_package_data=True,
)
