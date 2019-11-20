from setuptools import setup, find_packages

with open('requirements.in') as f:
    REQUIREMENTS = f.read().splitlines()

with open('VERSION') as f:
    VERSION = f.read()

setup(
    name="omnibot",
    version=VERSION,
    packages=find_packages(exclude=["test*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    author="Ryan Lane",
    author_email="rlane@lyft.com",
    description="A slack proxy and framework.",
    license="apache2",
    url="https://github.com/lyft/omnibot",
)
