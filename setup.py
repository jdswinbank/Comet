from distutils.core import setup
import comet

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="Comet",
    description=comet.__description__,
    author=comet.__author__,
    author_email=comet.__contact__,
    version=comet.__version__,
    url=comet.__url__,
    packages=[
        'comet',
        'comet.test',
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
