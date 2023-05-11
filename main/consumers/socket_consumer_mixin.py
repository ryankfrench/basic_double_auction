'''
core socket communication mixin
'''
import json
import logging
import sys

from asgiref.sync import sync_to_async

from channels.generic.websocket import AsyncWebsocketConsumer

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from main.models import SessionPlayer

class SocketConsumerMixin(AsyncWebsocketConsumer):
    '''
    core socket communication functions
    '''
    room_name = None
    room_group_name = None           #channel that consumer listens on
    channel_session_user = True
    http_user = True
    player_key = ""                  #SessionPlayer.player_key
    thread_sensitive = False

    async def connect(self):
        '''
        inital connection from websocket
        '''
        self.thread_sensitive = True if hasattr(sys, '_called_from_test') else False

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        
        kwargs = self.scope['url_route']['kwargs']
        room_name =  kwargs.get('room_name')
        page_key =  kwargs.get('page_key',"")
        
        self.player_key =  kwargs.get('player_key',"")

        #self.room_group_name = room_name + page_key
        self.room_group_name = f'{page_key}-{room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        result = await sync_to_async(take_handle_dis_connect, thread_sensitive=self.thread_sensitive)(self.player_key, True)

        #send updated connection status to all users
        await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_connection_status",
                 "data": result,
                 "sender_channel_name": self.channel_name,
                },
            )

        logger = logging.getLogger(__name__) 
        logger.info(f"SocketConsumerMixin Connect channel name: {self.channel_name}, room group name: {self.room_group_name}")

        await self.accept()

    async def disconnect(self, close_code):
        '''
        disconnect websockeet
        '''

        result = await sync_to_async(take_handle_dis_connect, thread_sensitive=False)(self.player_key, False)

        #send updated connection status to all users
        await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_connection_status",
                 "data": result,
                 "sender_channel_name": self.channel_name,
                },
            )
       
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        '''
        incoming data from websocket
        '''
        text_data_json = json.loads(text_data)

        message_type = text_data_json['message_type']    #name of child method to be called
        message_text = text_data_json['message_text']    #data passed to above method
        message_target = text_data_json.get('message_target', None)  #group or individual channel

        # Send message to target
        if not message_target or message_target == "self":
            await self.channel_layer.send(
                self.channel_name,
                {
                    'type': message_type,
                    'message_text': message_text
                }
            )
        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': message_type,
                    'message_text': message_text,
                    'sender_channel_name': self.channel_name,
                }
            )

def take_handle_dis_connect(connection_uuid, value):
    '''
    handle socket disconnect
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"take_handle_dis_connect: {connection_uuid} {value}")

    try:
        with transaction.atomic():
            session_player = SessionPlayer.objects.select_for_update().get(player_key=connection_uuid)
            session_player.connecting = False

            if value:
                session_player.connected_count += 1
            else:
                session_player.connected_count -= 1

            if session_player.connected_count < 0:
                session_player.connected_count = 0

            session_player.save()

        return {"value" : "success",  "result" : {"id" : session_player.id, "player_key" : f'{session_player.player_key}', "connected_count" : session_player.connected_count}}              

    except ObjectDoesNotExist:
        logger.info(f"take_handle_dis_connect session player not found: {connection_uuid} {value}")
        return {"value" : "fail",  "result" : {}}
