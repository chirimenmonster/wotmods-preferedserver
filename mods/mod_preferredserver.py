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

        
def overrideMethod(cls, method):
    def decorator(handler):
        orig = getattr(cls, method)
        newm = lambda *args, **kwargs: handler(orig, *args, **kwargs)
        if type(orig) is not property:
            setattr(cls, method, newm)
        else:
            setattr(cls, method, property(newm))
    return decorator


def getServerShortName(serverUrl):
    return g_preDefinedHosts.byUrl(serverUrl).shortName or i18n.makeString('#menu:login/auto')


def init():
    try:
        BigWorld.logInfo(MOD.NAME, '{0} {1} ({2})'.format(MOD.NAME, MOD.VERSION, MOD.SUPPORT_URL), None)
        Manager.AUTO_LOGIN_QUERY_ENABLED = False
        connectionMgr = dependency.instance(IConnectionManager)
        loginMgr = dependency.instance(ILoginManager)
        connectionMgr.onLoggedOn -= loginMgr._onLoggedOn

        @overrideMethod(Manager.Manager, '_onLoggedOn')
        def _onLoggedOn(base, *args, **kwargs):
            return _onLoggedOn_modified(base, *args, **kwargs)
        
        connectionMgr.onLoggedOn += loginMgr._onLoggedOn
    except:
        LOG_CURRENT_EXCEPTION()


def _onLoggedOn_modified(orig, self, responseData):
    try:
        serverName = self._preferences['server_name']
        serverShortName = getServerShortName(serverName)
        SystemMessages.pushMessage('{}: selected {}'.format(MOD.NAME, serverShortName))
        if self.wgcAvailable and self._Manager__wgcManager.onLoggedOn(responseData):
            self._preferences.clear()
            if serverName != AUTO_LOGIN_QUERY_URL:
                self._preferences['server_name'] = serverName
                BigWorld.logInfo(MOD.NAME, '_onLoggedOn: save server_name: {} ({})'.format(serverShortName, serverName), None)
            self._preferences.writeLoginInfo()
            return
    except:
        LOG_CURRENT_EXCEPTION()
    orig(self, responseData)


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
            if serverName is None:
                selectedServer = self._Manager__servers.selectedServer
                if not selectedServer:
                    BigWorld.logInfo(MOD.NAME, 'No server was selected when WGC connect happened, so return', None)
                    return
                serverName = selectedServer['data']
            self._preferences['server_name'] = serverName
            serverShortName = getServerShortName(serverName)
            BigWorld.logInfo(MOD.NAME, 'tryWgcLogin: set preference server_name: {} ({})'.format(serverShortName, serverName), None)
    except:
        LOG_CURRENT_EXCEPTION()
