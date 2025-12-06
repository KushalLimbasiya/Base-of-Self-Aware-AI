"""Setup for Atom AI Assistant package."""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'readme.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(req_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='atom-ai',
    version='2.0.0',
    author='Kushal Limbasiya & Meett Paladiya',
    description='Advanced self-aware AI personal assistant with natural language understanding',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/KushalLimbasiya/Base-of-Self-Aware-AI',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=read_requirements(),
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    entry_points={
        'console_scripts': [
            'atom=atom.main:main',  # Will add main() function
            'atom-train=train:main',  # Will add main() function
        ],
    },
)
