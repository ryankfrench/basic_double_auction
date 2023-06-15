'''
parameterset player type edit form
'''

from django import forms
from django.db.models.query import RawQuerySet

from main.models import ParameterSetPlayerType

class ParameterSetPlayerTypeForm(forms.ModelForm):
    '''
    parameterset player type edit form
    '''
    #type_id = forms.IntegerField(label='Type ID', widget=forms.TextInput(attrs={"v-model":"current_parameter_set_player_type.type_id",}))
    budget = forms.IntegerField(label='Budget',
                               widget=forms.TextInput(attrs={"v-model":"current_parameter_set_player_type.budget",}))
    
    units = forms.IntegerField(label='Units',
                               widget=forms.TextInput(attrs={"v-model":"current_parameter_set_player_type.units",}))

    class Meta:
        model=ParameterSetPlayerType
        fields =['budget', 'units']