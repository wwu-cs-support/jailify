from setuptools import setup, find_packages

requires = ["click", "python-magic"]

setup(
    name='jailify',
    version='1.0.1',
    description='Create and delete senior project jails',
    author='CS Support',
    author_email='cs.support@wwu.edu',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
    ],
    packages=find_packages(),
    package_data={},
    py_modules=['jailify'],
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'jailify=jailify.__main__:jailify_main',
            'dejailify=jailify.__main__:dejailify_main',
        ],
    },
)

