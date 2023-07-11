'''
parameterset player edit form
'''

from django import forms
from django.db.models.query import RawQuerySet

from main.models import ParameterSetPlayer
from main.models import ParameterSetPlayerType

class ParameterSetPlayerForm(forms.ModelForm):
    '''
    parameterset player edit form
    '''

    id_label = forms.CharField(label='Label Used in Chat',
                               widget=forms.TextInput(attrs={"v-model":"current_parameter_set_player.id_label",}))
    
    parameter_set_player_type = forms.ModelChoiceField(label='Player Type', 
                                                       queryset = ParameterSetPlayerType.objects.none())
                                                       #widget=forms.Select(attrs={"v-model":"current_parameter_set_player.parameter_set_player_type.id"}))

    def __init__(self, *args, **kwargs):
        parameter_set_id = kwargs.pop('parameter_set_id', None)
        super(ParameterSetPlayerForm, self).__init__(*args, **kwargs)
        if parameter_set_id:
            parameter_set_player_type = ParameterSetPlayerType.objects.filter(parameter_set_id=parameter_set_id)

    class Meta:
        model=ParameterSetPlayer
        fields =['id_label', 'parameter_set_player_type']
    
