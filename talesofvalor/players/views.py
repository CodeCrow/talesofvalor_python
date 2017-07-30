"""These are views that are used for viewing and editing player app.

REFERENCE:

https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
"""
from django.views.generic.edit import CreateView

from .models import Player

class PlayerCreateView(CreateView):
    model = Player
    fields = '__all__'