"""These are views that are used for viewing and editing player app.

REFERENCE:

https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#abstractbaseuser
"""
from django.views.generic.edit import CreateView, UpdateView, FormView

from .forms import UserForm, PlayerForm, RegistrationForm
from .models import Player

class PlayerCreateView(CreateView):
    model = Player
    fields = '__all__'

class PlayerUpdateView(UpdateView):
    model = Player
    fields = '__all__'

    def get_object(self):
        return Player.objects.get(user__username=self.kwargs['username']) # or request.POST

class RegistrationView(FormView):
    # We are making this too hard by tryig to link the 2 forms.
    # Just make one registration form (even if it has duplicates of the model fields!)
    # It will be easier and it will GET IT DONE.
    template_name = 'players/registration_form.html'
    form_class = RegistrationForm

    def get_success_url(self):
        return reverse('players:player_update')

    def get_context_data(self, **kwargs):
        data = super(RegistrationView, self).get_context_data(**kwargs)
        print "I'm getting context data"
        if self.request.POST:
            print "I'm postin'"
            data['user_form'] = UserForm(self.request.POST)
            data['player_form'] = PlayerForm(self.request.POST)
        else:
            data['user_form'] = UserForm(initial={"cp_available": 0})
            data['player_form'] = PlayerForm()
        return data
    def form_invalid(self, form):
        print "I'm fucked!"
        print form.errors
        return super(RegistrationView, self).form_invalid(form)

    def form_valid(self, form):
        print "is the form valid?"
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        context = self.get_context_data()
        result = super(ThemeCreate, self).form_valid(form)
        variants = context['variants']
        variants.instance = self.object
        try:
            project = Project.objects.get(pk=self.kwargs['pid'])
            self.object.project.add(project)
            self.object.save()
        except KeyError:
            pass
        for variant in variants.forms:
            variant.data["%s-theme" % (variant.prefix)] = self.object.id
        if variants.is_valid() and variants.has_changed():
            variants.save()
        else:
            print("dammit!  Variants are broken!")
            print variants.errors

        attributes = context['attributes']
        attributes.instance = self.object
        contenttype = ContentType.objects.get_for_model(self.object)
        for attribute in attributes.forms:
            attribute.data["%s-content_type" % (attribute.prefix)] = contenttype.id
            attribute.data["%s-object_id" % (attribute.prefix)] = self.object.id
        if attributes.is_valid():
            attributes.save()
        else:
            print("dammit!  Theme attributes are broken!")
            print attributes.errors

        # return result
        return super(RegistrationView, self).form_valid(form)

    def get_success_url(self):
        return reverse('player_detail', kwargs={'pk': self.object.username})