"""
These are views that are used for viewing and editing records
of a player attending an event.
"""
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView,\
    DeleteView
from django.views.generic import DetailView, ListView

from .models import Attendance


class AttendanceCreateView(PermissionRequiredMixin, CreateView):
    """
    Allows the creation of an attendance
    """
    model = Attendance
    fields = '__all__'
    permission_required = ('attendance.can_add', )
    success_url = reverse_lazy('attendance:attendance_list')


class AttendanceUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Edits an attendance that has already been entered.
    """

    model = Attendance
    fields = '__all__'
    permission_required = ('attendance.can_edit', )
    success_url = reverse_lazy('attendance:attendance_list')


class AttendanceDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Removes an attendance permanantly.

    If the attendance was the first attendance of a player, it also
    updates that field.
    """

    model = Attendance
    permission_required = ('attendance.can_delete', )
    success_url = reverse_lazy('attendance:attendance_list')


class AttendanceDetailView(PermissionRequiredMixin, DetailView):
    """
    Show the details for an origin.

    From here you can edit the details of a character or choose skills.
    """

    model = Attendance
    permission_required = ('attendance.can_edit', )
    fields = '__all__'



class AttendanceListView(PermissionRequiredMixin, ListView):
    """
    Show the details for a character.

    From here you can edit the details of a character or choose skills.
    """

    model = Attendance
    permission_required = ('attendance.can_edit', )
    paginate_by = 25
