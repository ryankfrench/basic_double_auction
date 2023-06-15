import logging

from asgiref.sync import sync_to_async

from django.core.exceptions import ObjectDoesNotExist

from main.models import Session
from main.models import ParameterSetPlayerType

from main.forms import ParameterSetPlayerTypeForm

from .get_parameter_set import take_get_parameter_set

class ParameterSetPlayerTypesMixin():
    '''
    parameter set player type mixin
    '''

    async def update_parameter_set_player_type(self, event):
        '''
        update a parameterset player type
        '''

        message_data = {}
        message_data["status"] = await take_update_parameter_set_player_type(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)

    async def remove_parameterset_player_type(self, event):
        '''
        remove a parameterset player type
        '''

        message_data = {}
        message_data["status"] = await take_remove_parameterset_player_type(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)
    
    async def add_parameterset_player_type(self, event):
        '''
        add a parameterset player type
        '''

        message_data = {}
        message_data["status"] = await take_add_parameterset_player_type(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)

@sync_to_async
def take_update_parameter_set_player_type(data):
    '''
    update parameterset player type
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset player type: {data}")

    session_id = data["session_id"]
    parameterset_player_type_id = data["parameterset_player_type_id"]
    form_data = data["form_data"]

    try:        
        parameter_set_player_type = ParameterSetPlayerType.objects.get(id=parameterset_player_type_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameter_set_player_type parameterset_player_type, not found ID: {parameterset_player_type_id}")
        return
    
    form_data_dict = form_data

    logger.info(f'form_data_dict : {form_data_dict}')

    form = ParameterSetPlayerTypeForm(form_data_dict, instance=parameter_set_player_type)

    if form.is_valid():         
        form.save()              
        parameter_set_player_type.update_json_local()

        return {"value" : "success"}                      
                                
    logger.info("Invalid parameterset player type form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

@sync_to_async
def take_remove_parameterset_player_type(data):
    '''
    remove the specifed parmeterset player type
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"Remove parameterset player type: {data}")

    session_id = data["session_id"]
    parameterset_player_type_id = data["parameterset_player_type_id"]

    try:        
        session = Session.objects.get(id=session_id)
        session.parameter_set.remove_player_type(parameterset_player_type_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_remove_parameterset_player_type paramterset_player_type, not found ID: {parameterset_player_type_id}")
        return
    
    return {"value" : "success"}

@sync_to_async
def take_add_parameterset_player_type(data):
    '''
    add a new parameter player type to the parameter set
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"Add parameterset player type: {data}")

    session_id = data["session_id"]

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_take_update_parameter_set session, not found ID: {session_id}")
        return {"value" : "fail"}

    session.parameter_set.add_player_type()

    return {"value" : "success"}
    
