import re
from setuptools import setup


requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()  # type: ignore

requirements.remove("furo")

version = ''
with open('deta/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)  # type: ignore

if not version:
    raise RuntimeError('version is not set')

if version.endswith(('a', 'b', 'rc')):
    try:
        import subprocess

        p = subprocess.Popen(['git', 'rev-list', '--count', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += out.decode('utf-8').strip()
        p = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += '+g' + out.decode('utf-8').strip()
    except Exception:  # noqa
        pass

setup(
    name='deta',
    version=version,
    description='Async API wrapper for Deta Base and Drive HTTP API',
    url='https://github.com/jnsougata/deta',
    author='Sougata Jana',
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
    install_requires=requirements,
    project_urls={
        'Source': 'https://github.com/jnsougata/deta',
    },
)
