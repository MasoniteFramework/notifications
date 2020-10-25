from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='masonite-notifications',
    package_dir={'': 'src'},
    packages=[
        'masonite.notifications',
        'masonite.notifications.components',
        'masonite.notifications.drivers',
        'masonite.notifications.snippets',
        'masonite.notifications.providers',
        'masonite.notifications.commands',
        'masonite.notifications.models',
    ],
    version='3.0.0',
    install_requires=[
        # TODO: when 3.0 officially released put it here
        # "masonite==3.0.0b1",
    ],
    description='Masonite Notifications Package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Joseph Mancuso',
    author_email='joe@masoniteproject.com',
    url='https://github.com/MasoniteFramework/notifications',
    license="MIT",
    keywords="Masonite, Python",
    classifiers=[],
    include_package_data=True,
    extras_require={
        "test": ["coverage", "pytest", "pytest-cov", "coveralls", "responses"],
        "dev": ["black", "flake8", "twine>=1.5.0", "wheel"],
        "services": ["pusher", "ably", "vonage"]
    },
)
