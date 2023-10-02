from setuptools import setup, find_packages

setup(
    name='uplaybook2',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'symbolicmode',
    ],
    entry_points={
        'console_scripts': [
            'up2=uplaybook2.internals:cli',
        ],
    },
)
