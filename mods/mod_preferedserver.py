from debug_utils import LOG_CURRENT_EXCEPTION
from gui.login.Servers import Servers

selected_idx = 1

def init():
    global orig_setServerList
    orig_setServerList = Servers._setServerList
    Servers._setServerList = _setServerList


def _setServerList(self, baseServerList):
    try:
        (hostName, friendlyName, csisStatus, peripheryID) = baseServerList[selected_idx]
        if not self._loginPreferences['server_name'] or self._loginPreferences['server_name'] != hostName:
            self._loginPreferences['server_name'] = hostName
            print 'set default server: {}, {}'.format(friendlyName, hostName)
    except:
        LOG_CURRENT_EXCEPTION()
    orig_setServerList(self, baseServerList)
