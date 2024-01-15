""" 
Serializers for the Comments
"""
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    
    content_type = serializers.CharField()
    object_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = [
            'content_type',
            'object_id',
            'created_by',
            'modified_by',
            'comment'
        ]

    def create(self, validated_data):
        # figure out the content type and put it in.
        content_type = ContentType.objects.get(model=validated_data.get('content_type'))
        validated_data['content_type'] = content_type
        # actually create and return the comment
        return Comment.objects.create(**validated_data)