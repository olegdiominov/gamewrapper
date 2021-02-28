from setuptools import setup

setup(
    name='gamewrapper',
    version='1.0',
    py_modules=['gamewrapper'],
    install_requires=['i3ipc'],
    entry_points={'console_scripts': ['gamewrapper=gamewrapper:main']}
)
