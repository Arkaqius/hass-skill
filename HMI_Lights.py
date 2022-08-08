from mycroft.skills.common_iot_skill import (IOT_REQUEST_ID, Action, Attribute,
                                             IoTRequest, IoTRequestVersion, State, Thing,
                                             _BusKeys)
from mycroft.skills.common_iot_skill import (IOT_REQUEST_ID, Action, Attribute,
                                             IoTRequest, IoTRequestVersion, State, Thing,
                                             _BusKeys)
import os
os.sys.path.append('/home/arek/_repos/mycroft-core/skills/hass-skill')
from HMI_Common import HMI_Candidates, HMI_dlg_rtn


SUPPORT_BRIGHTNESS = 1
SUPPORT_COLOR_TEMP = 2
SUPPORT_EFFECT = 4
SUPPORT_FLASH = 8
SUPPORT_COLOR = 16
SUPPORT_TRANSITION = 32
SUPPORT_WHITE_VALUE = 128
BRIGHNTESS_STEP = 25 # in %

def handle_request(request,HAS_inst):
    dlg_result = HMI_dlg_rtn.UNKNOWN
    #Create queary and find matchign candidates
    candidates = HMI_Candidates.find_candidates(   build_suggest_entity_name(request),
                                            HAS_inst.HA_entity_group_ligts)
    #Choose one or ask for more specific information
    w_en = choose_winner(candidates)
    #Determinate which action shall be run
    #Simple ON/OFF
    if(request.action.name == 'ON' or request.action.name == 'OFF'):
        dlg_result = handle_request_turn_onoff(request,w_en,HAS_inst)
    #Change brightness to exact value
    elif(request.action == Action.ADJUST and request.attribute == Attribute.BRIGHTNESS):
        dlg_result = handle_request_change_brightness(request,w_en,HAS_inst)
    #Increase brightness
    elif((request.action == Action.INCREASE and request.attribute == Attribute.BRIGHTNESS)):
        dlg_result = handle_request_increase_brightness(request,w_en,HAS_inst)
    #Decrease brightness
    elif((request.action == Action.DECREASE and request.attribute == Attribute.BRIGHTNESS)):
        dlg_result = handle_request_decrease_brightness(request,w_en,HAS_inst)
    #Binary queary
    elif((request.action == Action.BINARY_QUERY and request.state == State.POWERED)):
        dlg_result = handle_req_bq(request,w_en,HAS_inst)
    #Information queary - brightness
    elif((request.action == Action.INFORMATION_QUERY and request.attribute == Attribute.BRIGHTNESS)):
        dlg_result = handle_req_iq_brgth(request,w_en,HAS_inst)

    #Speak dialog
    if(HMI_dlg_rtn.UNKNOWN == dlg_result):
        HAS_inst.speak_dialog('General_Unknown')
    elif(HMI_dlg_rtn.SUCCESS == dlg_result):
        HAS_inst.speak_dialog('General_Success')
    elif(HMI_dlg_rtn.UF_BRIGHTNESS == dlg_result):
        HAS_inst.speak_dialog('LIGHT_UF_Bright',
                                {'feature'  :   'Brightness',
                                 'f_e_name' :   w_en.entity['entity_id']
                                })
    elif(HMI_dlg_rtn.NO_RESPONSE == dlg_result):
        pass #Response was done before

def handle_req_bq(request,w_en,HAS_inst):
    entity_id = w_en.entity['entity_id']
    state = HAS_inst.HA._get_state(entity_id)
    HAS_inst.speak_dialog('General_BQ',
                                {'entity_id':   entity_id,
                                 'state'    :   state["state"]
                                })
    return HMI_dlg_rtn.NO_RESPONSE

def handle_req_iq_brgth(request,w_en,HAS_inst):
    entity_id = w_en.entity['entity_id']
    state = HAS_inst.HA._get_state(entity_id)
    HAS_inst.speak_dialog('LIGHT_IQ_BRIGHTNESS',
                                {'friendly_name':   entity_id,
                                 'brg_level'    :   (float(state['attributes']['brightness']) * 100/256)
                                })
    return HMI_dlg_rtn.NO_RESPONSE

def handle_request_turn_onoff(request,w_en,HAS_inst):
    entity_id = w_en.entity['entity_id']
    HAS_inst.HA.execute_service('light','turn_'+str.lower(request.action.name),{'entity_id' : f'{entity_id}'})
    return HMI_dlg_rtn.SUCCESS

def handle_request_change_brightness(request,w_en,HAS_inst):
    ''' Handle changing brigtness to exact value'''
    #Check if found light support brightness
    if w_en.entity['attributes']['supported_features'] & SUPPORT_BRIGHTNESS:
        entity_id = w_en.entity['entity_id']
        HAS_inst.HA.execute_service(    'light',
                                        'turn_on',
                                            {'entity_id' : f'{entity_id}',
                                            'brightness_pct' : f'{request.value * 100}'})
        dialog_rtn = HMI_dlg_rtn.SUCCESS
    else:
        dialog_rtn = HMI_dlg_rtn.UF_BRIGHTNESS

    return dialog_rtn

def handle_request_increase_brightness(request,w_en,HAS_inst):
    entity_id = w_en.entity['entity_id']
    HAS_inst.HA.execute_service(    'light',
                                    'turn_on',
                                        {'entity_id' : f'{entity_id}',
                                        'brightness_step_pct' : f'{BRIGHNTESS_STEP}'})
    return HMI_dlg_rtn.SUCCESS

def handle_request_decrease_brightness(request,w_en,HAS_inst):
    entity_id = w_en.entity['entity_id']
    HAS_inst.HA.execute_service(    'light',
                                    'turn_on',
                                        {'entity_id' : f'{entity_id}',
                                        'brightness_step_pct' : f'{BRIGHNTESS_STEP * -1}'})
    return HMI_dlg_rtn.SUCCESS

def choose_winner(candidates):
    return max(candidates, key=lambda x: x.ratio)

def build_suggest_entity_name(request):
    description = ''
    location = ''
    if request.description:
        description =  '_'.join(list(request.description))
    if request.location:
        location = request.location.name
    #Common pattern: light.<location>_<description>_light
    query = 'light.' + location.lower() + '_' +  description + '_light'

    return query