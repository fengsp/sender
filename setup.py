"""
Sender
------

Sender is easy
``````````````

.. code:: python
    
    from sender import Mail, Message

    mail = Mail()

    msg = Message("title", sender="from@gmail.com")
    msg.body = "content"

    mail.send(msg)

Install
```````

.. code:: bash

    $ pip install sender

Links
`````

* `documentation <http://sender.readthedocs.org/>`_
* `github <https://github.com/fengsp/sender>`_
* `development version
  <http://github.com/fengsp/sender/zipball/master#egg=sender-dev>`_

"""
from setuptools import setup


setup(
    name='sender',
    version='0.1',
    url='https://github.com/fengsp/sender',
    license='BSD',
    author='Shipeng Feng',
    author_email='fsp261@gmail.com',
    description='Python SMTP Client for Humans',
    long_description=__doc__,
    py_modules= ['sender',],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
