import os, sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from distutils.core import setup

setup(
    name='mongodm',
    version='0.0.1',
    url='http://github.com/jean-philippe/mongodm',
    license='BSD',
    author='jean-philippe serafin',
    author_email='jean-philippe.serafin@dev-solutions.fr',
    description='just a mongodb document mapper, not a query layer',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=[
        'mongodm',
        'mongodm.ext'
    ],
    install_requires=[
        'pymongo>=1.9',
        'WTForms>=0.6.1'
    ]
)
