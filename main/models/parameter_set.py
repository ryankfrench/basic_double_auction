'''
parameter set
'''
import logging
import json

from decimal import Decimal

from django.db import models
from django.db.utils import IntegrityError
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ObjectDoesNotExist

from main import globals

from main.models import InstructionSet

import main

class ParameterSet(models.Model):
    '''
    parameter set
    '''    
    instruction_set = models.ForeignKey(InstructionSet, on_delete=models.CASCADE, related_name="parameter_sets")

    period_count = models.IntegerField(verbose_name='Number of periods', default=20)                          #number of periods in the experiment
    period_length = models.IntegerField(verbose_name='Period Length, Production', default=60           )      #period length in seconds
    
    private_chat = models.BooleanField(default=True, verbose_name='Private Chat')                          #if true subjects can privately chat one on one
    show_instructions = models.BooleanField(default=True, verbose_name='Show Instructions')                #if true show instructions

    survey_required = models.BooleanField(default=False, verbose_name="Survey Required")                      #if true show the survey below
    survey_link = models.CharField(max_length = 1000, default = '', verbose_name = 'Survey Link', blank=True, null=True)

    prolific_mode = models.BooleanField(default=False, verbose_name="Prolific Mode")                          #put study into prolific mode
    prolific_completion_link = models.CharField(max_length = 1000, default = '', verbose_name = 'Forward to Prolific after sesison', blank=True, null=True) #at the completion of the study forward subjects to link

    reconnection_limit = models.IntegerField(verbose_name='Age Warning', default=25)       #age cut that issues a warning for invalid age range

    test_mode = models.BooleanField(default=False, verbose_name='Test Mode')                                #if true subject screens will do random auto testing

    json_for_session = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)                   #json model of parameter set 

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set'
        verbose_name_plural = 'Parameter Sets'
    
    def from_dict(self, new_ps):
        '''
        load values from dict
        '''
        logger = logging.getLogger(__name__) 

        message = "Parameters loaded successfully."
        status = "success"

        try:
            self.period_count = new_ps.get("period_count")
            self.period_length = new_ps.get("period_length")

            self.private_chat = True if new_ps.get("private_chat") == "True" else False

            self.show_instructions = True if new_ps.get("show_instructions") == "True" else False

            self.survey_required = True if new_ps.get("survey_required") == "True" else False
            self.survey_link = new_ps.get("survey_link")

            self.prolific_mode = new_ps.get("prolific_mode", False)
            self.prolific_completion_link = new_ps.get("prolific_completion_link", None)

            self.reconnection_limit = new_ps.get("reconnection_limit", None)

            self.instruction_set = InstructionSet.objects.get(label=new_ps.get("instruction_set")["label"])

            self.save()

            #parameter set player types
            self.parameter_set_player_types.all().delete()

            new_parameter_set_player_types = new_ps.get("parameter_set_player_types")

            for i in new_parameter_set_player_types:
                t = main.models.ParameterSetPlayerType.objects.create(parameter_set=self)
                t.from_dict(new_parameter_set_player_types[i])

            #parameter set players
            self.parameter_set_players.all().delete()

            new_parameter_set_players = new_ps.get("parameter_set_players")

            for i in new_parameter_set_players:
                p = main.models.ParameterSetPlayer.objects.create(parameter_set=self)
                p.from_dict(new_parameter_set_players[i])

            self.update_player_count()

            self.json_for_session = None
            self.save()
            
        except IntegrityError as exp:
            message = f"Failed to load parameter set: {exp}"
            status = "fail"
            logger.warning(message)

        return {"status" : status, "message" :  message}

    def setup(self):
        '''
        default setup
        '''    
        self.add_player_type()
        self.add_player()
        

        self.json_for_session = None

        self.save()

        for i in self.parameter_set_players.all():
            i.setup()

    def add_player_type(self):
        '''
        add a parameterset player type
        '''

        player_type = main.models.ParameterSetPlayerType()
        player_type.parameter_set = self
        player_type.type_id = self.parameter_set_player_types.count() + 1
        player_type.budget = 0
        player_type.units = 0
        player_type.save()

        if (self.json_for_session):
            self.update_json_fk(update_player_types=True)
    
    def remove_player_type(self, parameterset_player_type_id):
        '''
        remove specified parameterset player type
        '''
        
        try:
            player = self.parameter_set_player_types.get(id=parameterset_player_type_id)
            player.delete()

        except ObjectDoesNotExist:
            logger = logging.getLogger(__name__) 
            logger.warning(f"parameter set remove_player, not found ID: {parameterset_player_type_id}")

        self.update_player_type_count()
        self.update_json_fk(update_player_types=True)
    
    def update_player_type_count(self):
        '''
        update the number of parameterset players
        '''
        for count, i in enumerate(self.parameter_set_player_types.all()):
            i.type_id = count + 1
            i.update_json_local()
            i.save()

    def add_player(self):
        '''
        add a parameterset player
        '''

        player = main.models.ParameterSetPlayer()
        player.parameter_set = self
        player.player_number = self.parameter_set_players.count() + 1
        player.id_label = player.player_number
        player.parameter_set_player_type = self.parameter_set_player_types.first()

        player.save()

        if (self.json_for_session):
            self.update_json_fk(update_players=True)
    
    def remove_player(self, parameterset_player_id):
        '''
        remove specified parameterset player
        '''
        
        try:
            player = self.parameter_set_players.get(id=parameterset_player_id)
            player.delete()

        except ObjectDoesNotExist:
            logger = logging.getLogger(__name__) 
            logger.warning(f"parameter set remove_player, not found ID: {parameterset_player_id}")

        self.update_player_count()
        self.update_json_fk(update_players=True)
    
    def update_player_count(self):
        '''
        update the number of parameterset players
        '''
        for count, i in enumerate(self.parameter_set_players.all()):
            i.player_number = count + 1
            i.update_json_local()
            i.save()
    
    def update_json_local(self):
        '''
        update json model
        '''

        self.json_for_session["id"] = self.id
                
        self.json_for_session["period_count"] = self.period_count

        self.json_for_session["period_length"] = self.period_length

        self.json_for_session["private_chat"] = "True" if self.private_chat else "False"
        self.json_for_session["show_instructions"] = "True" if self.show_instructions else "False"
        self.json_for_session["instruction_set"] = self.instruction_set.json_min()

        self.json_for_session["survey_required"] = "True" if self.survey_required else "False"
        self.json_for_session["survey_link"] = self.survey_link

        self.json_for_session["prolific_mode"] = "True" if self.prolific_mode else "False"
        self.json_for_session["prolific_completion_link"] = self.prolific_completion_link

        self.json_for_session["reconnection_limit"] = self.reconnection_limit

        self.json_for_session["test_mode"] = "True" if self.test_mode else "False"

        self.save()
    
    def update_json_fk(self, update_players=False, update_player_types=False):
        '''
        update json model
        '''
        if update_players:
            self.json_for_session["parameter_set_players_order"] = list(self.parameter_set_players.all().values_list('id', flat=True))
            self.json_for_session["parameter_set_players"] = {p.id : p.json() for p in self.parameter_set_players.all()}
        
        if update_player_types:
            self.json_for_session["parameter_set_player_types"] = {t.id : t.json() for t in self.parameter_set_player_types.all()}

        self.save()

    def json(self, update_required=False):
        '''
        return json object of model, return cached version if unchanged
        '''
        if not self.json_for_session or \
           update_required:
            self.json_for_session = {}
            self.update_json_local()
            self.update_json_fk(update_players=True, update_player_types=True)

        return self.json_for_session
    
    def get_json_for_subject(self):
        '''
        return json object for subject, return cached version if unchanged
        '''
        
        if not self.json_for_session:
            return None

        v = self.json_for_session

        v.pop("parameter_set_players")
        v.pop("parameter_set_players_order")
        
        return v
        

