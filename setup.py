import sys

# dirty hack, always use wheel
sys.argv.append('bdist_wheel')

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='rit.core',
    version='0.1',
    description='Core package for restaurant technologies',
    long_description=readme(),
    classifiers=[
        'Development Status :: 0.1 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Topic :: Restaurant :: IT technologies',
    ],
    url='https://github.com/sergeyglazyrindev/ritcore',
    author='Sergey Glazyrin',
    author_email='sergey.glazyrin.dev@gmail.com',
    license='MIT',
    install_requires=['wheezy.web==0.1.485', 'nose==1.3.7', 'lxml==3.4.4', ],
    package_dir={'': 'src'},
    namespace_packages=['rit'],
    include_package_data=True,
    zip_safe=False,
    packages=['rit.core', ]
)
