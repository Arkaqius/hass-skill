from mycroft.skills.common_iot_skill import (IOT_REQUEST_ID, Action, Attribute,
                                             IoTRequest, IoTRequestVersion, State, Thing,
                                             _BusKeys)
from mycroft.skills.common_iot_skill import (IOT_REQUEST_ID, Action, Attribute,
                                             IoTRequest, IoTRequestVersion, State, Thing,
                                             _BusKeys)
import os
os.sys.path.append('/home/arek/_repos/mycroft-core/skills/hass-skill')
from HMI_Common import  HMI_dlg_rtn

'''
Requirements:
- Change WW temperature
- Turn on/off WW
- Chaeck if it is on/off
- Check WW temeperature 

HASS preparing:
- WW water temperature
- WW water enable/disable
- WW water set temperature - input_selection
'''

def handle_request(request,HAS_inst):
    dlg_result = HMI_dlg_rtn.UNKNOWN

    #Determinate which action shall be run
    #Change WW temperature
    if(request.action == Action.SET or request.action == Action.ADJUST):
        dlg_result = req_set_WW_temp(request,HAS_inst)
    #Turn on/off WW
    elif(request.action == Action.ON or request.action == Action.OFF):
        dlg_result = req_turn_onoff_WW(request,HAS_inst)
    #Binary queary
    elif((request.action == Action.BINARY_QUERY and request.state == State.POWERED)):
        dlg_result = handle_req_bq_WW(request,HAS_inst)
    #Information queary - temperature
    elif((request.action == Action.INFORMATION_QUERY and request.attribute == Attribute.TEMPERATURE)):
        dlg_result = handle_req_iq_wwT(request,HAS_inst)

    #Speak dialog
    if(HMI_dlg_rtn.UNKNOWN == dlg_result):
        HAS_inst.speak_dialog('General_Unknown')
    elif(HMI_dlg_rtn.SUCCESS == dlg_result):
        HAS_inst.speak_dialog('General_Success')
    elif(HMI_dlg_rtn.NO_RESPONSE == dlg_result):
        pass #Response was done before

def req_set_WW_temp(request,HAS_inst):
    option = None
    if(request.value == 1):
        option = '40C - Economic'
    if(request.value == 2):
        option = '45C - Comfort'
    if(request.value == 3):
        option = '50C -Tube'    
    entity_id = HAS_inst.WW_set_temp_entity[0]['entity_id']
    HAS_inst.HA.execute_service('input_select',
                                'select_option',{
                                                    "entity_id": "input_select.warm_water_preset",
                                                    "option": "50C -Tube"
                                                })
    return HMI_dlg_rtn.SUCCESS

def req_turn_onoff_WW(request,HAS_inst):
    entity_id = HAS_inst.WW_enable_entity[0]['entity_id']
    HAS_inst.HA.execute_service(    'input_boolean',
                                    'turn_'+str.lower(request.action.name),
                                    {'entity_id' : f'{entity_id}'})
    return HMI_dlg_rtn.SUCCESS

def handle_req_bq_WW(request,HAS_inst):
    entity_id = HAS_inst.WW_enable_entity[0]['entity_id']
    state = HAS_inst.HA._get_state(entity_id)
    HAS_inst.speak_dialog('WW_BQ',
                                {'entity_id':   entity_id,
                                 'state'    :   state["state"]
                                })
    return HMI_dlg_rtn.NO_RESPONSE

def handle_req_iq_wwT(request,HAS_inst):
    entity_id = HAS_inst.WW_cur_temp_entity[0]['entity_id']
    state = HAS_inst.HA._get_state(entity_id)
    HAS_inst.speak_dialog('WW_IQ_TEMP',
                                {'temperature'    :   (state['state'])})
    return HMI_dlg_rtn.NO_RESPONSE