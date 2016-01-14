from __future__ import unicode_literals, division, print_function
import sys
from sqlalchemy import engine_from_config
from sqlalchemy.schema import MetaData
import argparse
import os
import os.path
import stat
import shutil
from pkg_resources import resource_filename
from alembic.config import Config
from alembic import command
from ivr.ivc.manager.user import User
from ivr.ivc.manager.access_key import AccessKeyManager, AccessKey
from ivr.ivc.daos.sa_dao_context_mngr import AlchemyDaoContextMngr
from ivr.ivc.daos.sa_user_dao import SAUserDao
from ivr.ivc.daos.sa_access_key_dao import SAAccessKeyDao
from ivr.common.exception import IVRError
from ivr.ivc.manager.user import PASSWORD_PBKDF2_HMAC_SHA256_SALT, UserManager
from passlib.utils.pbkdf2 import pbkdf2
import binascii
from ivr.common.utils import STRING, is_str


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


def add_user(config_uri, username, password_plain, title="default", desc="",
               flags=0, cellphone="", email="", user_type=User.USER_TYPE_NORMAL):
    config = configparser.ConfigParser()
    config.read(config_uri)
    settings = dict(config.items("alembic"))

    engine = engine_from_config(settings, 'sqlalchemy.')

    if is_str(password_plain):
        password_plain = password_plain.encode()

    password_hex = STRING(binascii.hexlify(pbkdf2(password_plain,
                                           PASSWORD_PBKDF2_HMAC_SHA256_SALT,
                                           100000,
                                           keylen=32,
                                           prf=str('hmac-sha256'))))
    dao_context_mngr = AlchemyDaoContextMngr(engine)
    user_dao = SAUserDao(dao_context_mngr)

    user_mngr = UserManager(user_dao=user_dao,
                            project_dao=None,
                            dao_context_mngr=dao_context_mngr)
    user_mngr.add_user(username=username,
                       password=password_hex,
                       title=title,
                       desc=desc,
                       flags=flags,
                       cellphone=cellphone,
                       email=email,
                       user_type=user_type)


def remove_user(config_uri, username):

    config = configparser.ConfigParser()
    config.read(config_uri)
    settings = dict(config.items("alembic"))

    engine = engine_from_config(settings, 'sqlalchemy.')

    dao_context_mngr = AlchemyDaoContextMngr(engine)
    user_dao = SAUserDao(dao_context_mngr)
    user_mngr = UserManager(user_dao=user_dao,
                            project_dao=None,
                            dao_context_mngr=dao_context_mngr)
    user_mngr.delete_user_by_name(username)


def add_access_key(config_uri, username, key_type=AccessKey.KEY_TYPE_NORMAL,
                   enabled=True, desc=""):

    config = configparser.ConfigParser()
    config.read(config_uri)
    settings = dict(config.items("alembic"))

    engine = engine_from_config(settings, 'sqlalchemy.')

    dao_context_mngr = AlchemyDaoContextMngr(engine)
    user_dao = SAUserDao(dao_context_mngr)
    access_key_dao = SAAccessKeyDao(dao_context_mngr)
    access_key_mngr = AccessKeyManager(
        access_key_dao=access_key_dao,
        user_dao=user_dao,
        dao_context_mngr=dao_context_mngr)
    access_key = access_key_mngr.new_access_key(
        username=username,
        key_type=key_type,
        enabled=enabled,
        desc=desc)

    return access_key



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


        parser = subparsers.add_parser('adduser',
                                       description='add a specified default user to the ivc database',
                                        help='add a specified default user to the ivc database ')
        parser.add_argument("-i", "--ini-file", help="the alembic ini configuration file of ivc, "
                                                     "default is ./ivc_alembic.ini",
                            default="./ivc_alembic.ini")


        parser.add_argument("-u", "--username", help="username of the new user , "
                                                     "Required",
                            type=STRING,
                            required=True)
        parser.add_argument("-p", "--password", help="plaintext password of the new user, "
                                                     "Required",
                            type=STRING,
                            required=True)
        parser.add_argument('-T', '--user-type', type=int, help="user type of the user(Default is 1:ADMIN)",
                            default=1)
        parser.add_argument('-t', '--title',
                            type=STRING,
                            help="title of the user(Default is username)")
        parser.add_argument('-d', '--desc',
                            type=STRING,
                            help="short desc of the user(Default is empty)",
                            default='')
        parser.add_argument('-e', '--email',
                            type=STRING,
                            help="email of the user(Default is empty)",
                            default='')
        parser.add_argument('-c', '--cellphone',
                            type=STRING,
                            help="cellphone number of the user(Default is empty)",
                            default='')
        parser.add_argument('-f', '--flags', type=int, help="flag of the user(Default is empty)",
                            default=0)
        parser.set_defaults(func=self.add_user)

        parser = subparsers.add_parser('rmuser',
                                       description='remove a specified user from the ivc database',
                                        help='remove a specified user from the ivc database ')
        parser.add_argument("-i", "--ini-file", help="the alembic ini configuration file of ivc, "
                                                     "default is ./ivc_alembic.ini",
                            default="./ivc_alembic.ini")


        parser.add_argument("-u", "--username",
                            type=STRING,
                            help="username of the new user , "
                                                     "Required",
                            required=True)

        parser.set_defaults(func=self.remove_user)


        parser = subparsers.add_parser('addkey',
                                       description='add a new access key to the ivc database',
                                        help='add a new access key to the ivc database ')
        parser.add_argument("-i", "--ini-file", help="the alembic ini configuration file of ivc, "
                                                     "default is ./ivc_alembic.ini",
                            default="./ivc_alembic.ini")


        parser.add_argument("-u", "--username",
                            type=STRING,
                            help="username of the new access key , "
                                                     "Required",
                            required=True)
        parser.add_argument('-T', '--key-type', type=int, help="key type of the new access key(Default is 1:PRIVILEGE)",
                            default=1)

        parser.add_argument('-d', '--desc',
                            type=STRING,
                            help="short desc of the access key(Default is empty)",
                            default='')
        parser.add_argument('--disabled', action='store_true', help="disable the new access key(Default is enabled)")

        parser.set_defaults(func=self.add_access_key)

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

    def add_user(self, args):
        if args.title is None:
            args.title = args.username
        # print(args)
        print("Add new user %s to DB" % args.username, end="......\n")
        add_user(config_uri=args.ini_file,
                 username=args.username,
                 password_plain=args.password,
                 title=args.title,
                 user_type=args.user_type,
                 desc=args.desc,
                 flags=args.flags,
                 email=args.email,
                 cellphone=args.cellphone)
        print("Done")

    def remove_user(self, args):
        print("Remove user %s from DB" % args.username, end="......\n")
        remove_user(config_uri=args.ini_file,
                    username=args.username)
        print("Done")

    def add_access_key(self, args):

        print("Add a new access key for user %s to DB" % args.username, end="......\n")
        access_key = add_access_key(config_uri=args.ini_file,
                                    username=args.username,
                                    key_type=args.key_type,
                                    desc=args.desc,
                                    enabled=not args.disabled)
        print("Done")
        print("new key(key_id:%s, secret:%s, username:%s, key_type:%d, enabled:%s, desc:%s)" % (
            access_key.key_id, access_key.secret, access_key.username, access_key.key_type,
            str(access_key.enabled), access_key.desc))

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