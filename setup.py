import sys

# dirty hack, always use wheel
sys.argv.append('bdist_wheel')

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()
# wheezy.web[mako]==0.1.485

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
    install_requires=['wheezy.web[mako]==0.1.485', 'nose==1.3.7', 'lxml==3.4.4',
                      'uWSGI==2.0.11.1', 'SQLAlchemy==1.0.8', 'Jinja2==2.8', 'restea==0.2.1',
                      'pg8000==1.10.2', 'python-dateutil==2.4.2', 'python3-memcached==1.51', 'factory-boy==2.6.1'],
    package_dir={'': 'src'},
    dependency_links=['http://github.com/sergeyglazyrindev/restea/tarball/master#egg=restea==0.2.1'],
    namespace_packages=['rit'],
    include_package_data=True,
    zip_safe=False,
    packages=['rit.core', ],
    scripts=['bin/notifyprojectchanged.sh', 'bin/rit-admin.py', 'bin/runcompass.sh', 'bin/start_work_on_project.sh']
)
