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
    dsn = {}
    for entry in 'dbname user password host port'.split():
        if cfg.has_option('Database', entry):
            el = cfg.get('Database', entry)
            if entry == 'port':
                dsn[entry] = int(el)
            else:
                dsn[entry] = el
    return dbms, adapter, dsn

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

def _SOCKET(cfg, conn, special, parameters):
    for entry in parameters.split():
        if cfg.has_option('Server', entry.lower()):
            el = cfg.get('Server', entry.lower())
            if entry != special:
                conn = "%s:%s=%s" % (conn, entry, el)
            else:
                conn = "%s:%s" % (conn, el)
    return conn
                
def _SSL(cfg):
    return _SOCKET(cfg, 'ssl', 'port', 'port privatekey certKey sslmethod interface backlog')

def _UNIX(cfg):
    return _SOCKET(cfg, 'unix', 'address', 'address mode backlog')

def _TCP(cfg):
    return _SOCKET(cfg, 'tcp', 'port', 'port interface backlog')

_disp = {'tcp':_TCP,
         'ssl':_SSL,
         'unix':_UNIX
        }

