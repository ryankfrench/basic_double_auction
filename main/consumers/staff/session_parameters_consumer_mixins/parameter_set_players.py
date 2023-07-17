import logging

from asgiref.sync import sync_to_async

from django.core.exceptions import ObjectDoesNotExist

from main.models import Session
from main.models import ParameterSetPlayer

from main.forms import ParameterSetPlayerForm

from ..session_parameters_consumer_mixins.get_parameter_set import take_get_parameter_set

class ParameterSetPlayersMixin():
    '''
    parameter set plaeyer mixin
    '''

    async def update_parameter_set_player(self, event):
        '''
        update a parameterset player
        '''

        message_data = {}
        message_data["status"] = await take_update_parameter_set_player(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)

    async def remove_parameterset_player(self, event):
        '''
        remove a parameterset player
        '''

        message_data = {}
        message_data["status"] = await take_remove_parameterset_player(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)
    
    async def add_parameterset_player(self, event):
        '''
        add a parameterset player
        '''

        message_data = {}
        message_data["status"] = await take_add_parameterset_player(event["message_text"])
        message_data["parameter_set"] = await take_get_parameter_set(event["message_text"]["session_id"])

        await self.send_message(message_to_self=message_data, message_to_group=None,
                                message_type="update_parameter_set", send_to_client=True, send_to_group=False)

@sync_to_async
def take_update_parameter_set_player(data):
    '''
    update parameterset player
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset player: {data}")

    session_id = data["session_id"]
    parameterset_player_id = data["parameterset_player_id"]
    form_data = data["form_data"]

    try:        
        parameter_set_player = ParameterSetPlayer.objects.get(id=parameterset_player_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameter_set_player parameterset_player, not found ID: {parameterset_player_id}")
        return
    
    form_data_dict = form_data
    form_data_dict["parameter_set_player_type"] = form_data_dict["parameter_set_player_type"]["id"]

    logger.info(f'form_data_dict : {form_data_dict}')

    form = ParameterSetPlayerForm(form_data_dict, instance=parameter_set_player)
    form.fields['parameter_set_player_type'].queryset = parameter_set_player.parameter_set.parameter_set_player_types.all()

    if form.is_valid():         
        form.save()              
        parameter_set_player.update_json_local()

        return {"value" : "success"}                      
                                
    logger.info("Invalid parameterset player form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

@sync_to_async
def take_remove_parameterset_player(data):
    '''
    remove the specifed parmeterset player
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"Remove parameterset player: {data}")

    session_id = data["session_id"]
    parameterset_player_id = data["parameterset_player_id"]

    try:        
        session = Session.objects.get(id=session_id)
        session.parameter_set.remove_player(parameterset_player_id)
        session.update_player_count()
    except ObjectDoesNotExist:
        logger.warning(f"take_remove_parameterset_player paramterset_player, not found ID: {parameterset_player_id}")
        return
    
    return {"value" : "success"}

@sync_to_async
def take_add_parameterset_player(data):
    '''
    add a new parameter player to the parameter set
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"Add parameterset player: {data}")

    session_id = data["session_id"]

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_take_update_parameter_set session, not found ID: {session_id}")
        return {"value" : "fail"}

    session.parameter_set.add_player()
    session.update_player_count()

    return {"value" : "success"}
    
