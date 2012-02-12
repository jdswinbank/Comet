import os
import distutils.sysconfig
from distutils.core import setup

setup(
    name="Comet",
    description="VOEvent Broker",
    author="John Swinbank",
    author_email="swinbank@transientskp.org",
    packages=[
        'comet',
        'comet.config',
        'comet.plugins',
        'comet.service',
        'comet.tcp',
        'comet.utility'
    ],
    scripts=['scripts/comet-sendvo'],
    package_data={'comet': ['schema/*.xsd']},
    data_files=[
        (
            os.path.join(
                distutils.sysconfig.get_python_lib(prefix=''),
                'twisted/plugins'
            ),
            [
                'twisted/plugins/broker_plugin.py',
                'twisted/plugins/subscriber_plugin.py'
            ]
        )
    ]
)
