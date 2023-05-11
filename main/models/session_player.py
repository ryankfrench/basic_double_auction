'''
session player model
'''

#import logging
import uuid
import logging

from decimal import Decimal

from django.db import models
from django.urls import reverse
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.core.exceptions import ObjectDoesNotExist

from main.models import Session
from main.models import ParameterSetPlayer
from main.models import Parameters

from main.globals import round_half_away_from_zero

import main

class SessionPlayer(models.Model):
    '''
    session player model
    '''
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="session_players")
    parameter_set_player = models.ForeignKey(ParameterSetPlayer, on_delete=models.CASCADE, related_name="session_players_paramterset")

    player_number = models.IntegerField(verbose_name='Player number', default=0)                        #player number, from 1 to N
    player_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Player Key')      #login and channel key
    connecting = models.BooleanField(default=False, verbose_name='Consumer is connecting')              #true when a consumer is connceting
    connected_count = models.IntegerField(verbose_name='Number of consumer connections', default=0)     #number of consumers connected to this subject

    name = models.CharField(verbose_name='Full Name', max_length = 100, default="", blank=True, null=True)              #subject's full name
    student_id = models.CharField(verbose_name='Student ID', max_length = 100, default="", blank=True, null=True)       #subject's student ID number
    email =  models.EmailField(verbose_name='Email Address', max_length = 100, blank=True, null=True)                   #subject's email address
    earnings = models.IntegerField(verbose_name='Earnings in cents', default=0)                         #earnings in cents
    name_submitted = models.BooleanField(default=False, verbose_name='Name submitted')                  #true if subject has submitted name and student id

    current_instruction = models.IntegerField(verbose_name='Current Instruction', default=0)                     #current instruction page subject is on
    current_instruction_complete = models.IntegerField(verbose_name='Current Instruction Complete', default=0)   #furthest complete page subject has done
    instructions_finished = models.BooleanField(verbose_name='Instructions Finished', default=False)             #true once subject has completed instructions

    survey_complete = models.BooleanField(default=False, verbose_name="Survey Complete")                 #subject has completed the survey  

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        
        verbose_name = 'Session Player'
        verbose_name_plural = 'Session Players'
        ordering = ['player_number']
        constraints = [            
            models.UniqueConstraint(fields=['session', 'email'], name='unique_email_session_player', condition=~Q(email="")),
        ]

    def reset(self, full_reset=True):
        '''
        reset player to starting state
        '''

        self.earnings = 0
        self.name = ""
        self.student_id = ""
        self.email = None
        self.name_submitted = False
        self.survey_complete = False

        self.current_instruction = 1
        self.current_instruction_complete = 0
        self.instructions_finished = False

        self.save()
    
    def start(self):
        '''
        start experiment
        '''

        self.reset()

        #session player periods
        session_player_periods = []

        for i in self.session.session_periods.all():
            session_player_periods.append(main.models.SessionPlayerPeriod(session_period=i, session_player=self))
        
        main.models.SessionPlayerPeriod.objects.bulk_create(session_player_periods)

    def get_instruction_set(self):
        '''
        return a proccessed list of instructions to the subject
        '''

        instructions = [i.json() for i in self.parameter_set_player.parameter_set.instruction_set.instructions.all()]
 
        for i in instructions:
            i["text_html"] = i["text_html"].replace("#player_number#", self.parameter_set_player.id_label)
            i["text_html"] = i["text_html"].replace("#player_count-1#", str(self.parameter_set_player.parameter_set.parameter_set_players.count()-1))

        return instructions
    
    def get_survey_link(self):
        '''
        get survey link
        '''

        if self.survey_complete:
            return ""
        
        p = Parameters.objects.first()

        link_string = f'{self.session.parameter_set.survey_link}?'
        link_string += f'session_id={self.session.id}&'
        link_string += f'player_label={self.parameter_set_player.id_label}&'
        link_string += f'player_number={self.player_number}&'        
        link_string += f'player_key={self.player_key}&'
        link_string += f'server_url={p.site_url}&'

        return link_string

    def json(self, get_chat=True):
        '''
        json object of model
        '''
        return{
            "id" : self.id,      
            "name" : self.name,
            "student_id" : self.student_id,   
            "email" : self.email,
            "name_submitted" : self.name_submitted,

            "earnings" : self.earnings,

            "player_number" : self.player_number,
            "player_key" : self.player_key,

            "login_link" : reverse('subject_home', kwargs={'player_key': self.player_key}),
            "connected_count" : self.connected_count,

            "parameter_set_player" : self.parameter_set_player.get_json_for_subject(),

            "chat_all" : [c.json_for_subject() for c in self.session_player_chats_c.filter(chat_type=main.globals.ChatTypes.ALL)
                                                                                   .order_by('-timestamp')[:100:-1]
                         ] if get_chat else [],
            "new_chat_message" : False,           #true on client side when a new un read message comes in

            "current_instruction" : self.current_instruction,
            "current_instruction_complete" : self.current_instruction_complete,
            "instructions_finished" : self.instructions_finished,

            "survey_complete" : self.survey_complete,
            "survey_link" : self.get_survey_link(),

        }
    
    def json_for_subject(self, session_player):
        '''
        json model for subject screen
        session_player_id : int : id number of session player for induvidual chat
        '''

        return{
            "id" : self.id,  

            "player_number" : self.player_number,

            "chat_individual" : [c.json_for_subject() for c in  main.models.SessionPlayerChat.objects \
                                                                            .filter(chat_type=main.globals.ChatTypes.INDIVIDUAL) \
                                                                            .filter(Q(Q(session_player_recipients=session_player) & Q(session_player=self)) |
                                                                                    Q(Q(session_player_recipients=self) & Q(session_player=session_player)))
                                                                            .order_by('-timestamp')[:100:-1]
                                ],

            "new_chat_message" : False,           #true on client side when a new un read message comes in

            "parameter_set_player" : self.parameter_set_player.get_json_for_subject(),
        }

    def json_min(self, session_player_notice=None):
        '''
        minimal json object of model
        '''

        return{
            "id" : self.id,    
        }
    
    def json_earning(self):
        '''
        return json object of earnings only
        '''
        return{
            "id" : self.id, 
            "earnings" : self.earnings,
        }
    
    def get_earnings_in_dollars(self):
        '''
        return earnings in dollar format
        '''

        return f'${(self.earnings/100):.2f}'


        