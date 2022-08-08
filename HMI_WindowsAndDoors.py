from mycroft.skills.common_iot_skill import (IOT_REQUEST_ID, Action, Attribute,
                                             IoTRequest, IoTRequestVersion, State, Thing,
                                             _BusKeys)
from mycroft.skills.common_iot_skill import (IOT_REQUEST_ID, Action, Attribute,
                                             IoTRequest, IoTRequestVersion, State, Thing,
                                             _BusKeys)
import os
os.sys.path.append('/home/arek/_repos/mycroft-core/skills/hass-skill')
from HMI_Common import  HMI_Candidates,HMI_dlg_rtn

'''
Requirements:
- Check door/window status
- List all open door/window
- List all close door/window
- Check safe states of doors\windows

HASS preparing:
- Doors contact list
- Windows contacts list
'''

def handle_request(request,HAS_inst):
    dlg_result = HMI_dlg_rtn.UNKNOWN
    #Create queary and find matchign candidates
    if(Thing.DOOR == request.thing):
        candidates = HMI_Candidates.find_candidates(   build_suggest_entity_name(request),
                                            HAS_inst.DW_doors_list)
    elif(Thing.WINDOW == request.thing):
        candidates = HMI_Candidates.find_candidates(   build_suggest_entity_name(request),
                                            HAS_inst.DW_windows_list)
    #Choose one or ask for more specific information
    w_en = choose_winner(candidates)
    #Determinate which action shall be run
    #Check door/window status
    if((request.action == Action.BINARY_QUERY and request.state == State.CLOSED)):
        dlg_result = handle_req_DW_BQ(request,HAS_inst,w_en)
    #Speak dialog
    if(HMI_dlg_rtn.UNKNOWN == dlg_result):
        HAS_inst.speak_dialog('General_Unknown')
    elif(HMI_dlg_rtn.SUCCESS == dlg_result):
        HAS_inst.speak_dialog('General_Success')
    elif(HMI_dlg_rtn.NO_RESPONSE == dlg_result):
        pass #Response was done before

def handle_req_DW_BQ(request,HAS_inst,w_en):
    entity_id = w_en.entity['entity_id']
    state = HAS_inst.HA._get_state(entity_id)
    trans_state = 'open' if 'on' == state["state"] else 'closed'
    HAS_inst.speak_dialog('General_BQ',
                                {'entity_id':   entity_id,
                                 'state'    :   trans_state
                                })
    return HMI_dlg_rtn.NO_RESPONSE

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
    query = 'binary_sensor.' + location.lower() + '_' +  description + '_contact_contact'

    return query
