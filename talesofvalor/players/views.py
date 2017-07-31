"""These are views that are used for viewing and editing player app.

REFERENCE:

https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
"""
from django.views.generic.edit import CreateView, UpdateView

from .models import Player

class PlayerCreateView(CreateView):
    model = Player
    fields = '__all__'

class PlayerUpdateView(UpdateView):
    model = Player
    fields = '__all__'

    def get_object(self):
        print "USERNAME:"
        print self.kwargs
        return Player.objects.get(user__username=self.kwargs['username']) # or request.POST