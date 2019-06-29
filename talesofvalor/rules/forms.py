'''
REFERENCE
http://adamalton.blogspot.com/2014/02/displaying-django-genericforeignkey-as.html
'''
import re
from django import forms

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

# these are the models that we can gather the requirements from
from .models import Rule
from talesofvalor.origins.models import Origin
from talesofvalor.skills.models import Header, Skill

class RuleForm(forms.ModelForm):
    """ Form for creating an AttachableNote. """
    
    #GenericForeignKey form field, will hold combined object_type and object_id
    generic_obj = forms.ChoiceField()
    
    def __init__(self, *args, **kwargs):
        super(RuleForm, self).__init__(*args, **kwargs)
        #combine object_type and object_id into a single 'generic_obj' field
        #getall the objects that we want the user to be able to choose from
        available_objects = list(Origin.objects.all()) #put your stuff here
        available_objects += list(Header.objects.all())
        available_objects += list(Skill.objects.all())
        #now create our list of choices for the <select> field
        object_choices = []
        for obj in available_objects:
            obj_type = ContentType.objects.get_for_model(obj.__class__)
            obj_id = obj.id
            form_value = "type:%s-id:%s" % (obj_type.id, obj_id) #e.g."type:12-id:3"
            display_text = "{} - {}".format(
                obj_type.__str__(),
                obj.__str__()
            )
            object_choices.append([form_value, display_text])
        self.fields['generic_obj'].choices = object_choices
        self.fields['generic_obj'].help_text = _("The requirement that must be met to have the new cost.")
    
    class Meta:
        model = Rule
        exclude = [
            'content_type',
            'object_id',
            'content_object',
        ]
    
    def save(self, *args, **kwargs):
        #get object_type and object_id values from combined generic_obj field
        object_string = self.cleaned_data['generic_obj']
        matches = re.match("type:(\d+)-id:(\d+)", object_string).groups()
        content_type_id = matches[0] #get 45 from "type:45-id:38"
        object_id = matches[1] #get 38 from "type:45-id:38"
        content_type = ContentType.objects.get(id=content_type_id)
        self.cleaned_data['content_type'] = content_type_id
        self.cleaned_data['object_id'] = object_id
        self.instance.content_type = content_type
        self.instance.object_id = object_id
        return super(RuleForm, self).save(*args, **kwargs)
