import ConfigParser as cp
import sys
import os.path as op

from twisted.python import log, util

from utils import util

try: __file__
except NameError: __file__ = sys.executable

def getNetworkParameters(filename):
    cfg = _parse(filename)
    socket = cfg.get('Server', 'socket')
    return _disp[socket](cfg)

def getDatabaseParameters(filename):
    cfg = _parse(filename)
    dbms = cfg.get('Database','dbms')
    adapter = cfg.get('Database', 'adapter')
    dsn = ''
    for entry in 'dbname user password host port'.split():
        if cfg.has_option('Database', entry):
            el = cfg.get('Database', entry)
            dsn = '%s %s=%s' % (dsn, entry, el)
    return dbms, adapter, dsn.strip()

def getRemoteShParameters(filename):
    cfg = _parse(filename)
    port = int(cfg.get('RemoteShell', 'port'))
    enabled = int(cfg.get('RemoteShell', 'enabled'))
    return enabled, port

def getApplicationParameters(filename):
    cfg = _parse(filename)
    theme = cfg.get('Application', 'theme')
    return theme

def _parse(filename):
    parser = cp.ConfigParser()
    path = util.sibpath(__file__, 'files')
    config_file = op.join(path, filename)
    log.msg("Parsing... %s" % config_file)
    parser.read(config_file)
    return parser

def _SSL(cfg):
    conn = 'ssl'
    for entry in 'port privatekey certKey sslmethod interface backlog'.split():
        if cfg.has_option('Server', entry.lower()):
            el = cfg.get('Server', entry.lower())
            if entry != 'port':
                conn = "%s:%s=%s" % (conn, entry, el)
            else:
                conn = "%s:%s" % (conn, el)
    return conn

def _UNIX(cfg):
    conn = 'unix'
    for entry in 'address mode backlog'.split():
        if cfg.has_option('Server', entry.lower()):
            el = cfg.get('Server', entry.lower())
            if entry != 'address':
                conn = "%s:%s=%s" % (conn, entry, el)
            else:
                conn = "%s:%s" % (conn, el)
    return conn


def _TCP(cfg):
    conn = 'tcp'
    for entry in 'port interface backlog'.split():
        if cfg.has_option('Server', entry.lower()):
            el = cfg.get('Server', entry.lower())
            if entry != 'port':
                conn = "%s:%s=%s" % (conn, entry, el)
            else:
                conn = "%s:%s" % (conn, el)
    return conn

_disp = {'tcp':_TCP,
         'ssl':_SSL,
         'unix':_UNIX
        }

