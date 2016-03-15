from setuptools import setup, find_packages

setup(
    name='jailify',
    version='0.1.0',
    description='Create and delete senior project jails',
    author='CS Support',
    author_email='cs.support@wwu.edu',
    packages=find_packages(),
    package_data={},
    py_modules=['jailify'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'jailify=jailify.__main__:jailify_main',
            'dejailify=jailify.__main__:dejailify_main',
        ],
    },
)

