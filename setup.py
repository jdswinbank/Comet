from distutils.core import setup
import sys
import comet

with open('requirements%s.txt' % (sys.version_info.major,)) as f:
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
        'comet.handler',
        'comet.handler.test',
        'comet.log',
        'comet.log.test',
        'comet.plugins',
        'comet.plugins.test',
        'comet.protocol',
        'comet.protocol.test',
        'comet.service',
        'comet.service.test',
        'comet.utility',
        'comet.utility.test',
        'comet.validator',
        'comet.validator.test',
        'twisted'
    ],
    scripts=['scripts/comet-sendvo'],
    package_data={
        'comet': ['schema/*.xsd'],
        'comet.handler.test': [
            'test_spawn.sh',
            'test_spawn_failure.sh',
            'test_spawn_output.sh',
            'test_spawn_stdout.sh'
        ],
        'twisted': ['plugins/comet_plugin.py']
    },
    install_requires=required
)
