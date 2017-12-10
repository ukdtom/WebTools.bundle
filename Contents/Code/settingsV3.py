######################################################################################################################
#	Settings helper unit for WebTools
#
#	Author: dane22, a Plex Community member
#
######################################################################################################################

import json
import sys
import consts

GET = ['GETSETTINGS']
PUT = ['SETSETTING']
POST = ['SETPWD']
DELETE = ['']


class settingsV3(object):

    @classmethod
    def init(self):
        return

    ''' Get the relevant function and call it with optinal params '''
    @classmethod
    def getFunction(self, metode, req):
        self.init()
        params = req.request.uri[8:].upper().split('/')
        self.function = None
        if metode == 'get':
            for param in params:
                if param in GET:
                    self.function = param
                    break
                else:
                    pass
        elif metode == 'post':
            for param in params:
                if param in POST:
                    self.function = param
                    break
                else:
                    pass
        elif metode == 'put':
            for param in params:
                if param in PUT:
                    self.function = param
                    break
                else:
                    pass
        elif metode == 'delete':
            for param in params:
                if param in DELETE:
                    self.function = param
                    break
                else:
                    pass
        if self.function == None:
            Log.Debug('Function to call is None')
            req.clear()
            req.set_status(404)
            req.finish('Unknown function call')
        else:
            # Check for optional argument
            paramsStr = req.request.uri[req.request.uri.upper().find(
                self.function) + len(self.function):]
            # remove starting and ending slash
            if paramsStr.endswith('/'):
                paramsStr = paramsStr[:-1]
            if paramsStr.startswith('/'):
                paramsStr = paramsStr[1:]
            # Turn into a list
            params = paramsStr.split('/')
            # If empty list, turn into None
            if params[0] == '':
                params = None
            try:
                Log.Debug('Function to call is: ' + self.function +
                          ' with params: ' + str(params))
                if params == None:
                    getattr(self, self.function)(req)
                else:
                    getattr(self, self.function)(req, params)
            except Exception, e:
                Log.Exception('Exception in process of: ' + str(e))

    #********** Functions below ******************

    ''' Change the local auth password '''
    @classmethod
    def SETPWD(self, req, *args):
        Log.Debug('Recieved a call for setPwd')
        try:
            req.clear()
            try:
                # Get the Payload
                data = json.loads(req.request.body.decode('utf-8'))
            except Exception, e:
                req.set_status(412)
                req.finish('Not a valid payload?')
            else:
                # Get entry for old pwd
                if 'OldPwd' in data:
                    # Did it match?
                    if data['OldPwd'] == Dict['password']:
                        if 'NewPwd' in data:
                            # Save new Pwd
                            Dict['password'] = data['NewPwd']
                            Dict.Save
                            req.set_status(200)
                            req.finish("Password saved")
                        else:
                            req.set_status(412)
                            req.finish('Missing NewPwd')
                    else:
                        req.set_status(401)
                        req.finish('Old Password did not match')
                else:
                    req.set_status(412)
                    req.finish('Missing oldPwd parameter')
        except Exception, e:
            Log.Exception('Error in setPwd: ' + str(e))
            req.clear()
            req.set_status(e.code)
            req.finish(str(e))
            return req

    ''' Set the value of a specific setting '''
    @classmethod
    def SETSETTING(self, req, *args):
        Log.Debug('Recieved a call for putSetting')
        try:
            req.clear()
            try:
                # Get the Payload
                data = json.loads(req.request.body.decode('utf-8'))
            except Exception, e:
                req.set_status(412)
                req.finish('Not a valid payload?')
            else:
                if len(data) > 0:
                    for key in data:
                        Log.Debug('Saving: ' + str(key) +
                                  ' with a value of: ' + str(data[key]))
                        Dict[key] = data[key]
                    Dict.Save()
                    consts.consts.setConsts()
                    req.set_status(200)
                    req.finish("Setting saved")
                else:
                    req.set_status(412)
                    req.finish('Not a valid payload?')
        except Exception, e:
            Log.Exception('Error in putSetting: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish(str(e))

    # Return the value of a specific setting
    @classmethod
    def GETSETTINGS(self, req, *args):
        Log.Debug('Recieved a call for getSettings')
        try:
            req.clear()
            if not args:
                try:
                    mySetting = {}
                    mySetting['options_hide_integrated'] = (
                        Dict['options_hide_integrated'] == 'true')
                    mySetting['options_hide_local'] = (
                        Dict['options_hide_local'] == 'true')
                    mySetting['options_only_multiple'] = (
                        Dict['options_only_multiple'] == 'true')
                    mySetting['items_per_page'] = int(Dict['items_per_page'])
                    try:
                        mySetting['wt_csstheme'] = Dict['wt_csstheme']
                    except:
                        mySetting['wt_csstheme'] = ''
                    try:
                        mySetting['UILanguage'] = Dict['UILanguage']
                    except:
                        mySetting['UILanguage'] = 'en'
                    Log.Debug('Returning settings as %s' % (mySetting))
                    req.clear()
                    req.set_status(200)
                    req.set_header(
                        'Content-Type', 'application/json; charset=utf-8')
                    req.finish(json.dumps(mySetting))
                    return req
                except Exception, e:
                    Log.Exception('Error in getSettings: ' + str(e))
                    req.clear()
                    req.set_status(e.code)
                    req.finish(str(e))
            else:
                name = list(args)[0][0]
                if name in Dict:
                    retVal = Dict[name]
                    Log.Debug('Returning %s' % (retVal))
                    req.set_status(200)
                    req.set_header(
                        'Content-Type', 'application/json; charset=utf-8')
                    req.finish(json.dumps(retVal))
                else:
                    Log.Debug('Variable %s not found' % (name))
                    req.set_status(404)
                    req.finish('Setting not found')
        except Exception, e:
            Log.Exception('Error in getSettings: ' + str(e))
            req.clear()
            req.set_status(500)
            req.finish(str(e))
