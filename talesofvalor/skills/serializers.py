""" Serializers for the skills and headers """
from rest_framework.serializers import ModelSerializer

from .models import Header, Skill


class SkillSerializer(ModelSerializer):
    
    class Meta:
        model = Skill
        fields = [
            'name',
            'description',
        ]
