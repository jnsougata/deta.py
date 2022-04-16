import pathlib
from setuptools import setup, find_packages


here = pathlib.Path(__file__).parent.resolve()

with open('README.rst') as f:
    readme = f.read()


setup(
    name='aiotube',
    version='0.0.1',
    description='async API wrapper for deta.sh',
    long_description=readme,
    long_description_content_type="text/x-rst",
    url='https://github.com/jnsougata/async-deta',
    author='jnsougata',
    author_email='jnsougata@gmail.com',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    keywords='deta.sh',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.8.0',
    install_requires=['aiohttp'],
    project_urls={
        'Source': 'https://github.com/jnsougata/aisync-deta',
    },
)
