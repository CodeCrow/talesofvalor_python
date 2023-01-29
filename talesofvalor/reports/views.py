"""
Views for displaying reports of important information about the game.
"""
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.views.generic import ListView

from talesofvalor.events.models import Event
from talesofvalor.players.models import Registration


class ReportListView(PermissionRequiredMixin, ListView):
    permission_required = ('players.view_any_player', )
    model = Registration
    
    def get_queryset(self):
        """
        if the event id is set, get the information for that event.
        If it isn't get the latest event id
        """        
        queryset = super().get_queryset()
        # filter by event
        event_id = self.kwargs.get('event_id', None)
        if not event_id:
            event_id = Event.next_event().id
        queryset = queryset.filter(event__id=event_id)

        return queryset

    def get_context_data(self, **kwargs):
        '''
        Grab the event for this list
        '''
        # get the context data to add to.
        context_data = super().get_context_data(**kwargs)
        # set up the forms that appear in the list 
        event_id = self.kwargs.get('event_id', None)
        if not event_id:
            event_id = Event.next_event().id
        context_data['event'] = Event.objects.get(pk=event_id)
        # return the resulting context
        return context_data


class DiningReportListView(ReportListView):
    '''
    List information about players regarding food
    '''
    template_name = 'reports/diningreport_list.html'

    def get_queryset(self):
        """
        Set up the query set for the dining report.
        We only want to display registrations that are on the meal plan.
        """
        queryset = super().get_queryset()
        queryset = queryset.filter(mealplan_flag=True)
        return queryset


class RegistrationReportListView(ReportListView):
    '''
    List generalized information about user who are coming to a game.
    '''
    template_name = 'reports/registrationreport_list.html'
