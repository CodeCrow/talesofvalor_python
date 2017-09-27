"""These are views that are used for viewing and editing characters."""
from django.views.generic.edit import CreateView, UpdateView

from .models import Character

class CharacterCreateView(CreateView):
    model = Character
    fields = '__all__'

class CharacterUpdateView(UpdateView):
    model = Character
    fields = '__all__'