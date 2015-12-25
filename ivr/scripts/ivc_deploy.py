from __future__ import unicode_literals, division, print_function
import sys
from sqlalchemy import engine_from_config
from sqlalchemy.schema import MetaData
from streamswitch.wsgiapp.models import Base
import argparse
from streamswitch.exceptions import StreamSwitchError
import os
import os.path
import stat
import shutil
from pkg_resources import resource_filename
from alembic.config import Config
from alembic import command

if sys.version_info[:2] < (3, 0):
    import ConfigParser as configparser
else:
    import configparser


def initialize_db(config_uri):

    # setup_logging(config_uri)
    # settings = get_appsettings(config_uri, options=options)

    config = configparser.ConfigParser()
    config.read(config_uri)
    settings = dict(config.items("alembic"))

    engine = engine_from_config(settings, 'sqlalchemy.')
    # delete all tables

    meta = MetaData()
    meta.reflect(bind=engine)
    meta.drop_all(engine)


    upgrade_db(config_uri)


def upgrade_db(config_uri):
    alembic_cfg = Config(config_uri)
    command.upgrade(alembic_cfg, "head")


class DeloyCommand(object):


    description = """
This is a tools to help deploying ivc into your linux environment,
which provides many sub commands to fulfill different deploy tasks.
using:

    ivc_deploy.py sub-command -h

to print the options description for each command
    """
    def __init__(self):


        self.parser = argparse.ArgumentParser(description=self.description,
                                              formatter_class=argparse.RawDescriptionHelpFormatter)
        subparsers = self.parser.add_subparsers(help='sub-command help',
                                                title='subcommands',
                                                description='valid subcommands')



        parser = subparsers.add_parser('initdb',
                                       description='initialize the database (remove any data) '
                                                   'specified in the configure file by sqlalchemy ',
                                       help='initialize the database (remove any data) ')
        parser.add_argument("-i", "--ini-file", help="the alembic ini configuration file of ivc, "
                                                     "default is ./ivc_alembic.ini",
                            default="./ivc_alembic.ini")
        parser.set_defaults(func=self.initdb)

        parser = subparsers.add_parser('upgradedb',
                                       description='upgrade the database in the config to '
                                                   'the latest schema, and keep the original db data',
                                        help='upgrade the database by Sqlalchemy  ')
        parser.add_argument("-i", "--ini-file", help="the alembic ini configuration file of ivc, "
                                                     "default is ./ivc_alembic.ini",
                            default="./ivc_alembic.ini")
        parser.set_defaults(func=self.upgradedb)

        self.args = self.parser.parse_args()


    def initdb(self, args):
        # print(args)
        ini_conf_file = args.ini_file
        config = configparser.ConfigParser()
        config.read(ini_conf_file)
        print("Initialize DB %s " % config.get("alembic", "sqlalchemy.url"), end="......\n")
        initialize_db(ini_conf_file)
        print("Done")

    def upgradedb(self, args):
        # print(args)
        ini_conf_file = args.ini_file
        config = configparser.ConfigParser()
        config.read(ini_conf_file)
        print("Upgrade DB %s " % config.get("alembic", "sqlalchemy.url"), end="......\n")
        upgrade_db(ini_conf_file)
        print("Done")

    def run(self):

        if "func" not in self.args:
            self.parser.print_help()
            sys.exit(-1)

        return self.args.func(self.args)


def main(argv=sys.argv):
    command = DeloyCommand()
    return command.run()


if __name__ == '__main__': # pragma: no cover
    sys.exit(main() or 0)