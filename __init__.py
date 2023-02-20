from nturl2path import url2pathname
from mycroft import MycroftSkill, intent_file_handler
import mycroft.skills.common_iot_skill as IoTSkill 
from mycroft.skills.common_iot_skill import (IOT_REQUEST_ID, Action, Attribute,
                                             IoTRequest, IoTRequestVersion, State, Thing,
                                             _BusKeys)
from .ha_client import HomeAssistantClient
from mycroft.util.log import LOG
import os
os.sys.path.append('/opt/mycroft/skills/hass-skill')
import HMI_Lights
import HMI_WarmWater
import HMI_WindowsAndDoors

class Hass(IoTSkill.CommonIoTSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        #-------------------------------------------------------------------------------
        #Get settings
        url     = self.settings.get('host')
        port    = self.settings.get('port')
        token   = self.settings.get('token')
        #HOME ASSISTANT INTERFACE
        if('invalid' not in token):
            self.HA = HomeAssistantClient(url,port,token,ssl = True)
            self.ha_state = self.HA._get_state()

            '''
            Hass need to expose:
            -Light integration:
                - List of all lights
            -Warm water integration:
                - Enable/disable entitiy
                - Set temperature entity
                - Current temperature entity
            '''
            #Common entities types
            self.HA_entity_group_ligts  = [x for x in self.ha_state if x['entity_id'].split('.')[0] == 'light']
            self.WW_enable_entity       = [x for x in self.ha_state if x['attributes'].get('mc_name') == 'mc_WW_enable']
            self.WW_set_temp_entity     = [x for x in self.ha_state if x['attributes'].get('mc_name')  == 'mc_WW_set_temp']
            self.WW_cur_temp_entity     = [x for x in self.ha_state if x['attributes'].get('mc_name')  == 'mc_WW_cur_temp']
            self.DW_doors_list          = [ x for x in self.ha_state if                         \
                                            x['entity_id'].split('.')[0] == 'binary_sensor' and \
                                            'door_contact_contact' in x['entity_id'].split('.')[1]]
            self.DW_windows_list        = [ x for x in self.ha_state if                         \
                                            x['entity_id'].split('.')[0] == 'binary_sensor' and \
                                            'window_contact_contact' in x['entity_id'].split('.')[1]]
        #--------------------------------------------------------------------------------

    @property
    def supported_request_version(self) -> IoTRequestVersion:
        return IoTRequestVersion.V3

    @intent_file_handler('hass.intent')
    def handle_hass(self, message):
        self.speak_dialog('hass')

    def can_handle(self, request: IoTRequest):
        return True, None #TODO

    def run_request(self, request: IoTRequest, callback_data: dict):
        if(Thing.LIGHT == request.thing):
            HMI_Lights.handle_request(request,self)
        elif(Thing.WARM_WATER == request.thing):
            HMI_WarmWater.handle_request(request,self)
        elif(Thing.WINDOW == request.thing or Thing.DOOR == request.thing):
            HMI_WindowsAndDoors.handle_request(request,self)

def create_skill(): 
    return Hass()

