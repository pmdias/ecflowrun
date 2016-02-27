from setuptools import setup, find_packages
import ecflowrun


setup(
    name='ecflowrun',
    version=ecflowrun.__version__,
    description='Ecflow helpers',
    license='MIT License',
    author='Pedro Dias',
    author_email='pedrodias.miguel@gmail.com',
    maintainer='Pedro Dias',
    maintainer_email='pedrodias.miguel@gmail.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ecflow_admin = ecflowrun.server.admin:ecflow_admin',
        ]
    },
)
