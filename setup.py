from setuptools import setup

setup(
    name='masonite-notifications',
    package_dir={'': 'src'},
    packages=[
        'masonite.notifications',
        'masonite.notifications.components',
        'masonite.notifications.snippets',
        'masonite.notifications.providers',
        'masonite.notifications.commands',
    ],
    version='2.0.0',
    install_requires=[],
    description='Masonite Notifications for the Masonite framework',
    author='Joseph Mancuso',
    author_email='joe@masoniteproject.com',
    url='https://github.com/MasoniteFramework/notifications',
    keywords=['python web framework', 'python3', 'masonite'],
    classifiers=[],
    include_package_data=True,
)
