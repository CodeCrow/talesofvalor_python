"""These are views that are used for viewing and editing characters."""
from django.views.generic.edit import CreateView, UpdateView

from .models import Character

class CharacterCreateView(CreateView):
    model = Character
    fields = '__all__'

    def get_initial(self):
        # Get the initial dictionary from the superclass method
        initial = super(CharacterCreateView, self).get_initial()
        # Copy the dictionary so we don't accidentally change a mutable dict
        initial = initial.copy()
        initial['player'] = self.request.GET['player']
           # etc...
        return initial

class CharacterUpdateView(UpdateView):
    model = Character
    fields = '__all__'