import setuptools

with open('sentinellib/__init__.py') as fh:
    for line in fh:
        if line.find('__version__') >= 0:
            version = line.split('=')[1].strip()
            version = version.strip('"')
            version = version.strip("'")

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='sentinellib',
    version=version,
    description='Sentinel data access tools',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ShevFA/sentinellib',
    author='Shevelev Fedor',
    author_email='shevelyov@scanex.ru',
    classifiers=['Programming Language :: Python :: 3.9'],
    packages=['sentinellib'],
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=['requests', 'geojson', 'geomet']
)
