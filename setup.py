from distutils.core import setup

setup(
    name='pytago',
    version='0.0.1',
    packages=['pytago'],
    url='https://github.com/nottheswimmer/pytago',
    license='',
    author='Michael Phelps',
    author_email='michaelphelps@nottheswimmer.org',
    description='Transpiles some Python into human-readable Golang.',
    entry_points={
        'console_scripts': ['pytago=pytago.cmd:main'],
    },
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
