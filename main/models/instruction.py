'''
instructions
'''

#import logging

from django.db import models

from tinymce.models import HTMLField

from main.models import InstructionSet

class Instruction(models.Model):
    '''
    instruction model
    '''

    instruction_set = models.ForeignKey(InstructionSet, on_delete=models.CASCADE, related_name="instructions")

    text_html = HTMLField(default="Text here", verbose_name="Page HTML Text")
    page_number = models.IntegerField(verbose_name='Page Number', default=1)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.page_number}"

    class Meta:
        
        verbose_name = 'Instruction Page'
        verbose_name_plural = 'Instruction Pages'
        ordering = ['page_number']
        
    #return json object of class
    def json(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,         

            "page_number" : self.page_number,
            "text_html" : self.text_html,
        }
        