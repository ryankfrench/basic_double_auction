'''
parameterset player type
'''

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder

#from main.models import ParameterSet

import main

class ParameterSetPlayerType(models.Model):
    '''
    session player type parameters 
    '''

    parameter_set = models.ForeignKey("main.ParameterSet", on_delete=models.CASCADE, related_name="parameter_set_player_types")

    type_id = models.IntegerField(verbose_name='Type ID', default=0)         #player type id from 1 to M
    budget = models.IntegerField(verbose_name='Budget', default=0)           #budget in cents
    units = models.IntegerField(verbose_name='Units', default=0)             #units

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        verbose_name = 'Parameter Set Player Type'
        verbose_name_plural = 'Parameter Set Player Types'
        ordering=['type_id']

    def from_dict(self, new_ps):
        '''
        copy source values into this period
        source : dict object of parameterset player type
        '''

        self.type_id = new_ps.get("type_id")
        self.budget = new_ps.get("budget")
        self.units = new_ps.get("units")

        self.save()
        
        message = "Parameter Set Player Type loaded successfully."

        return message
    
    def setup(self):
        '''
        default setup
        '''    
        self.save()
    
    def update_json_local(self):
        '''
        update parameter set json
        '''
        self.parameter_set.json_for_session["parameter_set_player_types"][self.id] = self.json()
        self.parameter_set.save()

        self.save()

    def json(self):
        '''
        return json object of model
        '''
        
        return{

            "id" : self.id,
            "type_id" : self.type_id,
            "budget" : self.budget,
            "units" : self.units,
        }