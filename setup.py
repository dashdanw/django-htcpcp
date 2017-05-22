from distutils.core import setup
setup(
  name='django-htcpcp',
  packages=[
    'djhtcpcp',
    'djhtcpcp.middleware'
   ],
  install_requires=[
        'setuptools',
        'Django>=1.8'
   ],
  version='0.1.3',
  description='Django HyperText Coffee Pot Protocol Middleware (HTCPCP)',
  author='Dash Winterson',
  author_email='dashdanw@gmail.com',
  url='https://github.com/dashdanw/django-htcpcp',
  download_url='https://github.com/dashdanw/django-htcpcp/archive/0.1.1.tar.gz',
  keywords=['htcpcp', 'django', 'middleware', 'RFC 2324'],
  classifiers=[],
)