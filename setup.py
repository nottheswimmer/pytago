from distutils.core import setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pytago',
    version='0.0.9',
    packages=['pytago', 'pytago.go_ast', 'pytago.go_ast.bindings'],
    url='https://github.com/nottheswimmer/pytago',
    license='',
    author='Michael Phelps',
    author_email='michaelphelps@nottheswimmer.org',
    description='Transpiles some Python into human-readable Golang.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': ['pytago=pytago.cmd:main'],
    },
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
    include_package_data=True,
)
