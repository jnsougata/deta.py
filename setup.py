import pathlib
from setuptools import setup, find_packages


here = pathlib.Path(__file__).parent.resolve()

with open('README.md') as f:
    readme = f.read()


setup(
    name='deta',
    version='0.0.5',
    description='Async API wrapper for deta base and drive',
    long_description=readme,
    long_description_content_type="text/markdown",
    url='https://github.com/jnsougata/deta',
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
    keywords=['deta.sh', 'deta', 'api', 'wrapper', 'async'],
    packages=["deta"],
    python_requires='>=3.8.0',
    install_requires=['aiohttp'],
    project_urls={
        'Source': 'https://github.com/jnsougata/deta',
    },
)
