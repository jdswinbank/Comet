from distutils.core import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="Comet",
    description="VOEvent Broker",
    author="John Swinbank",
    author_email="swinbank@transientskp.org",
    url="http://comet.transientskp.org/",
    version="1.0.3",
    packages=[
        'comet',
        'comet.test',
        'comet.config',
        'comet.log',
        'comet.log.test',
        'comet.plugins',
        'comet.plugins.test',
        'comet.service',
        'comet.service.test',
        'comet.tcp',
        'comet.tcp.test',
        'comet.utility',
        'comet.utility.test',
        'twisted'
    ],
    scripts=['scripts/comet-sendvo'],
    package_data={
        'comet': ['schema/*.xsd'],
        'comet.utility.test': ['test_spawn.sh'],
        'twisted': ['plugins/comet_plugin.py']
    },
    install_requires=required
)
