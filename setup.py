from distutils.core import setup
import djhtcpcp
import pypandoc

setup(
    name='django-htcpcp',
    packages=[
      'djhtcpcp'
     ],
    install_requires=[
          'setuptools',
          'Django>=1.8'
     ],
    version=djhtcpcp.__version__,
    description='Django HyperText Coffee Pot Protocol Middleware (HTCPCP)',
    author='Dash Winterson',
    author_email='dashdanw@gmail.com',
    url='https://github.com/dashdanw/django-htcpcp',
    download_url='https://github.com/dashdanw/django-htcpcp/archive/{}.tar.gz'.format(djhtcpcp.__version__),
    keywords=[
      'htcpcp',
      'django',
      'middleware',
      'RFC 2324',
      'coffee'
    ],
    classifiers=[],
    long_description=pypandoc.convert('README.md', 'rst')
)