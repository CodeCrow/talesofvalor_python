"""
Describes the player models.

These models describe the player and its relationship to the
django authentication user models.
"""
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _

from djangocms_text_ckeditor.fields import HTMLField

from talesofvalor.events.models import Event, EventRegistrationItem,\
    EVENT_MEALPLAN_PRICE

REQUESTED = 'requested'
PENDING = 'pending'
COMPLETE = 'complete'
REFUSED = 'refused'
REQUEST_STATUS_CHOICES = (
    (REQUESTED, 'Requested'),
    (PENDING, 'Pending'),
    (COMPLETE, 'Complete'),
    (REFUSED, 'Refused'),
)

class Player(models.Model):
    """
    Player of a game.

    An individual who is playing a game.  All users are players
    of some sort.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    game_started = models.ForeignKey(Event, blank=True, null=True, on_delete=models.CASCADE)
    cp_available = models.PositiveIntegerField(default=0)
    staff_attention_flag = models.BooleanField(default=False)

    def __str__(self):
        """General display of model."""
        return "{} {}".format(
            self.user.first_name,
            self.user.last_name
        )

    @property
    def active_character(self):
        """
        The active character of the Player.

        Gets the active character from the list of characters associated with
        this player.

        TODO:
        if there is more than one character returned here, it should error
        out (try/except) The error should set the player to
        "needs attention flag".
        There should be a message added to the message queue explaining what
        happened. Or an email, since we don't have the request object
        to use with the messages framework.
        """
        try:
            return self.character_set.get(active_flag=True)
        except ObjectDoesNotExist:
            self.staff_attention_flag = True
            return None
        except MultipleObjectsReturned:
            self.staff_attention_flag = True
            return self.character_set.first()

    class Meta:
        """Add permissions."""

        permissions = (
            ("change_any_player", "Can change any player"),
            ("view_any_player", "Can view any player"),
        )


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    A User has been created.

    When a user is created, we also have to create a profile object and attach
    it to the user.  This uses the 'post_save' signal.
    """
    if created:
        Player.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    A User has been updated.

    When a user has been updated, we have to make sure that the profile
    attached to it has as well.  This uses the 'post_save' signal.
    """
    instance.player.save()


class RegistrationRequest(models.Model):
    """
    This is the request that a user has to register and is used to link the
    player to an eventRegistrationItem, which binds up different order
    possibiilities.

    Once the paypal transaction comes back, it will be used to produce
    the actual registrations.
    """
    event_registration_item = models.ForeignKey(
        EventRegistrationItem,
        on_delete=models.CASCADE
    )
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    mealplan_flag = models.BooleanField(default=False)
    vehicle_make = models.CharField(max_length=10, blank=True, default='')
    vehicle_model = models.CharField(max_length=15, blank=True, default='')
    vehicle_color = models.CharField(max_length=10, blank=True, default='')
    vehicle_registration = models.CharField(
        max_length=10,
        blank=True,
        default=''
    )
    local_contact = models.CharField(
        max_length=16,
        blank=True,
        default='',
        help_text=_("On site contact, such as a cell phone.")
    )
    notes = models.TextField(blank=True, default='')
    status = models.TextField(
        default=REQUESTED,
        choices=REQUEST_STATUS_CHOICES,
        help_text=_("Status of the request in ToV system.")
    )
    # information about Paypal order status
    paypal_order_id = models.TextField(
        blank=True,
        default='',
        help_text=_("Order recieved from PayPal system.")
    )   
    requested = models.DateTimeField(
        _('date created'),
        null=True,
        auto_now_add=True,
        editable=False
    )

    def cost(self):
        """
        Figure out the cost of this request based on field values.
        """
        mealplan_price = 0
        if self.mealplan_flag:
            mealplan_price = self.event_registration_item.events.count() * EVENT_MEALPLAN_PRICE
        return self.event_registration_item.price + mealplan_price


class Registration(models.Model):
    """
    Registration for events.

    Holds the registration for players for a specific event.

    This doesn't just link to the Registration request information because
    it is assumed that it might change on a per registration basis.
    """

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registration_request = models.ForeignKey(
        RegistrationRequest,
        null=True,
        on_delete=models.CASCADE,
    )
    cabin = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text=_("What cabin is the player staying in?")
    )
    mealplan_flag = models.BooleanField(
        default=False,
        help_text=_("Has the player signed up for a meal plan?")
    )
    notes = models.TextField(blank=True, default='')

    def save(self, *args, **kwargs):
        """
        Save the registration.

        When we do this, we should copy items from the previous registrations
        as a starting point if those fields are not filled in.
        """
        previous_registration = type(self).objects\
            .filter(
                event__event_date__lt=self.event.event_date,
                player=self.player
            )\
            .order_by('-event__event_date')\
            .first()
        if self.pk is None and previous_registration:
            # if this is new registration and not an update, take information
            # from the previous one if it isn't updated.
            if not self.cabin:
                self.cabin = previous_registration.cabin

        super(Registration, self).save(*args, **kwargs)


class PEL(models.Model):
    """
    (P)ost (E)vent (L)etter.

    Letter and information describing a player's experience at an event.
    """

    RATINGS_CHOICES = (
        (5, 'Amazing'),
        (4, 'Good'),
        (3, 'Average'),
        (2, 'Fair'),
        (1, 'Poor'),
    )

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    created = models.DateTimeField(
        _('date created'),
        null=True,
        auto_now_add=True,
        editable=False
    )
    modified = models.DateTimeField(
        _('last updated'),
        null=True,
        auto_now=True,
        editable=False
    )
    likes = models.TextField(blank=True, default='')
    dislikes = models.TextField(blank=True, default='')
    best_moments = models.TextField(blank=True, default='')
    worst_moments = models.TextField(blank=True, default='')
    learned = models.TextField(blank=True, default='')
    data = HTMLField(blank=True, default='')
    rating = models.PositiveIntegerField(choices=RATINGS_CHOICES)
