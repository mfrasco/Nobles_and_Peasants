from setuptools import setup

setup(
    name='Nobles_and_Peasants',
    packages=['Nobles_and_Peasants'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_login',
        'flask_bcrypt'
    ],
)
