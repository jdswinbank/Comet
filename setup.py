from distutils.core import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="Comet",
    description="VOEvent Broker",
    author="John Swinbank",
    author_email="swinbank@transientskp.org",
    url="http://comet.transientskp.org/",
    version="1.0.4",
    packages=[
        'comet',
        'comet.test',
        'comet.config',
        'comet.plugins',
        'comet.plugins.test',
        'comet.service',
        'comet.service.test',
        'comet.tcp',
        'comet.tcp.test',
        'comet.utility',
        'comet.utility.test',
        'comet.validator',
        'comet.validator.test',
        'comet.handler',
        'comet.handler.test',
        'twisted'
    ],
    scripts=['scripts/comet-sendvo'],
    package_data={
        'comet': ['schema/*.xsd'],
        'comet.handler.test': ['test_spawn.sh'],
        'twisted': ['plugins/comet_plugin.py']
    },
    install_requires=required
)
