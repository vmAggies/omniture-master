from setuptools import setup, find_packages

exec(open('omniture/version.py').read())
setup(name='omniture',
      description='A wrapper for the Adobe Analytics (Omniture and SiteCatalyst) web analytics API.',
      long_description=open('README.md').read(),
      version=__version__,
      license='MIT',
      packages=find_packages(),
      keywords='data analytics api wrapper adobe omniture',
      install_requires=[
            'requests',
            'python-dateutil',
      ],
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering :: Information Analysis',
                   ],
      )
