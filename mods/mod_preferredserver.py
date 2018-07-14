"""WoT mod to select preferred server"""

import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.login import Manager
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.login_manager import ILoginManager

class MOD:
    """mod's information"""
    AUTHOR = '${author}'
    NAME = '${name}'
    VERSION = '${version}'
    DESCRIPTION = '${description}'
    SUPPORT_URL = '${support_url}'

class ServiceLocator(object):
    connectionMgr = dependency.descriptor(IConnectionManager)
    loginMgr = dependency.descriptor(ILoginManager)

def init():
    try:
        BigWorld.logInfo(MOD.NAME, '{0} {1} ({2})'.format(MOD.NAME, MOD.VERSION, MOD.SUPPORT_URL), None)
        Manager.AUTO_LOGIN_QUERY_ENABLED = False
        Manager.Manager._onLoggedOn_modified = Manager_onLoggedOn_modified
        loginMgr = ServiceLocator.loginMgr
        ServiceLocator.connectionMgr.onLoggedOn -= loginMgr._onLoggedOn
        ServiceLocator.connectionMgr.onLoggedOn += loginMgr._onLoggedOn_modified
    except:
        LOG_CURRENT_EXCEPTION()


def Manager_onLoggedOn_modified(self, responseData):
    try:
        if self.wgcAvailable and self._Manager__wgcManager.onLoggedOn(responseData):
            serverName = self._preferences['server_name']
            self._preferences.clear()
            self._preferences['server_name'] = serverName
            self._preferences.writeLoginInfo()
            BigWorld.logInfo(MOD.NAME, 'save server_name: {}'.format(serverName), None)
            return
    except:
        LOG_CURRENT_EXCEPTION()
    self._onLoggedOn(responseData)
