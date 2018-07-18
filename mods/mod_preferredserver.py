"""WoT mod to select preferred server"""

import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION
from gui import SystemMessages
from gui.login import Manager
from helpers import dependency
from helpers import i18n
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.login_manager import ILoginManager
from predefined_hosts import g_preDefinedHosts, AUTO_LOGIN_QUERY_URL

class MOD:
    """mod's information"""
    AUTHOR = '${author}'
    NAME = '${name}'
    VERSION = '${version}'
    DESCRIPTION = '${description}'
    SUPPORT_URL = '${support_url}'

def _OverrideMethod(handler, cls, method):
    orig = getattr(cls, method)
    newm = lambda *a, **k: handler(orig, *a, **k)
    if type(orig) is not property:
        setattr(cls, method, newm)
    else:
        setattr(cls, method, property(newm))
        
def overrideMethod(*a, **k):
    def decorator2(handler):
        _OverrideMethod(handler, *a, **k)
    return decorator2

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


def getServerShortName(serverUrl):
    return g_preDefinedHosts.byUrl(serverUrl).shortName or i18n.makeString('#menu:login/auto')

def Manager_onLoggedOn_modified(self, responseData):
    try:
        serverName = self._preferences['server_name']
        serverShortName = getServerShortName(serverName)
        SystemMessages.pushMessage('{}: selected {}'.format(MOD.NAME, serverShortName))
        if self.wgcAvailable and self._Manager__wgcManager.onLoggedOn(responseData):
            self._preferences.clear()
            if serverName != AUTO_LOGIN_QUERY_URL:
                self._preferences['server_name'] = serverName
                BigWorld.logInfo(MOD.NAME, 'onLoggedOn: save server_name: {} ({})'.format(serverShortName, serverName), None)
            self._preferences.writeLoginInfo()
            return
    except:
        LOG_CURRENT_EXCEPTION()
    self._onLoggedOn(responseData)
    

@overrideMethod(Manager.Manager, 'initiateRelogin')
def initiateRelogin(orig, self, login, token2, serverName):
    try:
        self._preferences['server_name'] = serverName
        serverShortName = getServerShortName(serverName)
        BigWorld.logInfo(MOD.NAME, 'initiateRelogin: set preference server_name: {} ({})'.format(serverShortName, serverName), None)
    except:
        LOG_CURRENT_EXCEPTION()
    orig(self, login, token2, serverName)

@overrideMethod(Manager.Manager, 'tryWgcLogin')
def tryWgcLogin(orig, self, serverName = None):
    orig(self, serverName)
    try:
        if self.wgcAvailable:
            self._preferences['server_name'] = serverName
            serverShortName = getServerShortName(serverName)
            BigWorld.logInfo(MOD.NAME, 'tryWgcLogin: set preference server_name: {} ({})'.format(serverShortName, serverName), None)
    except:
        LOG_CURRENT_EXCEPTION()
