"""
Describes the player models.

These models describe the player and its relationship to the
django authentication user models.
"""
from taggit.managers import TaggableManager

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from djangocms_text_ckeditor.fields import HTMLField

from talesofvalor.events.models import Event, EventRegistrationItem,\
    EVENT_MEALPLAN_PRICE

REQUESTED = 'requested'
PENDING = 'pending'
COMPLETE = 'complete'
DENIED = 'denied'
REQUEST_STATUS_CHOICES = (
    (REQUESTED, 'Requested'),
    (PENDING, 'Pending'),
    (COMPLETE, 'Complete'),
    (DENIED, 'Denied'),
)

CAST = 'cast'
PLAYER = 'player'
REGISTRATION_TYPE_CHOICES = (
    (CAST, 'Cast'),
    (PLAYER, 'Player'),
)


class Player(models.Model):
    """
    Player of a game.

    An individual who is playing a game.  All users are players
    of some sort.

    If you are adding a new field here (e.g., pronouns), it
    also needs to be added to the registration view.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    game_started = models.ForeignKey(Event, blank=True, null=True, on_delete=models.CASCADE)
    cp_available = models.PositiveIntegerField(default=0)
    staff_attention_flag = models.BooleanField(default=False)
    player_pronouns = models.CharField(max_length=25, blank=True, null=True)
    food_allergies = models.TextField(default='', blank=True)

    def __str__(self):
        """General display of model."""
        player_string = "{} {}".format(
            self.user.first_name,
            self.user.last_name
        )
        if self.player_pronouns:
            player_string = "{} ({})".format(
                player_string,
                self.player_pronouns
            )
        return player_string

    class Meta:
        ordering = ("user__last_name", "user__first_name")

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

    @property
    def cabin(self):
        """
        Gets what the 'current' cabin should be based on 
        the registration of the previous event they attended.
        """
        previous_event = Registration.objects.filter(player=self)\
            .order_by("-event__event_date").first()
        if previous_event:
            return previous_event.cabin
        return None

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
    try:
        instance.player.save()
    except ObjectDoesNotExist:
        # maybe throw an error or just create the player.
        create_user_profile(User, instance, True)
        pass


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
    vegan_flag = models.BooleanField(
        _('Vegan Meal Requested'),
        default=False
    )
    vegetarian_flag = models.BooleanField(
        _('Vegetarian Meal Requested'),
        default=False
    ) 
    food_allergies = models.CharField(max_length=200, blank=True, default='')  
    no_car_flag = models.BooleanField(
        _('No car on site.'),
        default=False
    )    
    site_transportation = models.TextField(
        _('Came to site with/by'),
        blank=True,
        default='',
        help_text=_("The person or method you got to site with:  Uber, player name.  In case of emergencies.")
    )
    vehicle_make = models.CharField(max_length=10, blank=True, default='')
    vehicle_model = models.CharField(max_length=15, blank=True, default='')
    vehicle_color = models.CharField(max_length=10, blank=True, default='')
    vehicle_registration = models.CharField(
        _('License Plate'),
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
    # alternate payment types
    pay_at_door_flag = models.BooleanField(
        _('Payment brought to game'),
        default=False
    )
    already_paid_flag = models.BooleanField(
        _('Paid by another method.'),
        default=False
    ) 
    requested = models.DateTimeField(
        _('date created'),
        null=True,
        auto_now_add=True,
        editable=False
    )

    def __str__(self):
        """General display of model."""
        return mark_safe("{} &ndash; {} {}".format(
            self.event_registration_item,
            self.player.user.first_name,
            self.player.user.last_name
        ))

    def cost(self):
        """
        Figure out the cost of this request based on field values.
        """
        mealplan_price = 0
        if self.mealplan_flag:
            mealplan_price = self.event_registration_item.events.count() * EVENT_MEALPLAN_PRICE
        return self.event_registration_item.price + mealplan_price

    @classmethod
    def request_complete(cls, request_id, user, request):
        """
        Complate the request and make the registrations
        """
        event_reg_request = RegistrationRequest.objects.get(
            pk=request_id
        )
        # Create the event registration for each of the events that the
        # event_reg_request.eventregistrationitem is attached to.
        # create an email message for each registration
        email_connection = mail.get_connection()
        # create the list of messages
        email_messages = []
        for event in event_reg_request.event_registration_item.events.all():
            registration = Registration(
                player=user.player,
                event=event,
                no_car_flag=event_reg_request.no_car_flag,
                site_transportation=event_reg_request.site_transportation,
                vehicle_make=event_reg_request.vehicle_make,
                vehicle_model=event_reg_request.vehicle_model,
                vehicle_color=event_reg_request.vehicle_color,
                vehicle_registration=event_reg_request.vehicle_registration,
                local_contact=event_reg_request.local_contact,
                registration_request=event_reg_request,
                mealplan_flag=event_reg_request.mealplan_flag,
                food_allergies=event_reg_request.food_allergies,
                vegetarian_flag=event_reg_request.vegetarian_flag,
                vegan_flag=event_reg_request.vegan_flag,
                pay_at_door_flag=event_reg_request.pay_at_door_flag,
                already_paid_flag=event_reg_request.already_paid_flag,
                )
            registration.save()
            # send an email to staff with a link to the registration
            # send email using the self.cleaned_data dictionary
            message = """
            Hello!

            {} {} has a new registration for event {}.

            See it here:
            {}

            --ToV MechCrow
            """.format(
                    user.first_name,
                    user.last_name,
                    event.name,
                    request.build_absolute_uri(
                        reverse("registration:detail", kwargs={
                            'pk': registration.id
                        })
                    )
                )
            email_message = mail.EmailMessage(
                "Registration for {} {}".format(
                    user.first_name,
                    user.last_name
                ),
                message,
                settings.DEFAULT_FROM_EMAIL,
                ["rob@crowbringsdaylight.com", "wyldharrt@gmail.com", "ambisinister@gmail.com"]
            )
            email_messages.append(email_message)
        # send an email to each of them.
        email_connection.send_messages(email_messages)
        # close the connection to the email server
        email_connection.close()


class Registration(models.Model):
    """
    Registration for events.

    Holds the registration for players for a specific event.

    This doesn't just link to the Registration request information because
    it is assumed that it might change on a per registration basis.
    """

    PAYPAL = 'Paid (PayPal)'
    PAID_OTHER = 'Paid (other)'
    PAY_AT_DOOR = 'Pay at door'
    UNPAID = 'No arrangements'

    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registration_type = models.CharField(
        max_length=10,
        choices=REGISTRATION_TYPE_CHOICES,
        default=PLAYER
    )
    registration_request = models.ForeignKey(
        RegistrationRequest,
        null=True,
        blank=True,
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
    vegan_flag = models.BooleanField(
        _('Vegan Meal Requested'),
        default=False
    )
    vegetarian_flag = models.BooleanField(
        _('Vegetarian Meal Requested'),
        default=False
    )
    food_allergies = models.CharField(max_length=200, blank=True, default='')
    no_car_flag = models.BooleanField(
        _('No car on site.'),
        default=False
    )    
    site_transportation = models.TextField(
        _('Alternative Transportation'),
        blank=True,
        default='',
        help_text=_("The person or method you got to site with:  Uber, player name.  In case of emergencies.")
    )
    vehicle_make = models.CharField(max_length=10, blank=True, default='')
    vehicle_model = models.CharField(max_length=15, blank=True, default='')
    vehicle_color = models.CharField(max_length=10, blank=True, default='')
    vehicle_registration = models.CharField(
        _('License Plate'),
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
    # alternate payment types that might require interaction
    pay_at_door_flag = models.BooleanField(
        _('Payment brought to game'),
        default=False
    )
    already_paid_flag = models.BooleanField(
        _('Paid by another method.'),
        default=False
    ) 

    def __str__(self):
        """General display of model."""
        return mark_safe("{} &ndash; {} {}".format(
            self.event,
            self.player.user.first_name,
            self.player.user.last_name
        ))

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

    @property
    def payment_type(self):
        """
        Indicate how the event was paid for
        """
        if self.registration_request and self.registration_request.paypal_order_id:
            return self.PAYPAL
        if self.pay_at_door_flag:
            return self.PAY_AT_DOOR
        if self.already_paid_flag:
            return self.PAID_OTHER
        return self.UNPAID
    
    class Meta:
        """Add permissions."""

        permissions = (
            ("register_as_cast", "Can register as cast"),
        )


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
    # number of points players get for submitting a pel on time
    ON_TIME_BONUS = 2

    character = models.ForeignKey('characters.Character', on_delete=models.CASCADE)
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
    donations_time = models.TextField(
        _('Donations (Time spent doing set up / breakdown.'),
        blank=True,
        default=''
    )
    donations_props = models.TextField(
        _('Donations (Props/funds/or other materials.'),
        blank=True,
        default=''
    )
    rating = models.PositiveIntegerField(null=True, choices=RATINGS_CHOICES)
    favorites = models.TextField(
        _('What did you enjoy?'),
        blank=True,
        default=''
    )
    suggestions = models.TextField(
        _('What do you think could be improved?'),
        blank=True,
        default=''
    )
    plans = models.TextField(
        _("""What are you character's current interests and plans? What do
        you think you'll be working on moving forward?"""),
        blank=True,
        default=''
    )
    devout = models.TextField(
        _("""If you are Devout or Supplicant to a faith, please tell us 
        how you practiced and demonstrated your beliefs."""),
        blank=True,
        default=''
    )
    new_rule_likes = models.TextField(
        _("""Is there anything you really liked about the new rules and
        systems we've implemented?"""),
        blank=True,
        default=''
    )
    new_rule_dislikes = models.TextField(
        _("""Is there anything you didn't care for about the new rules and
        systems and what do you think would improve it?"""),
        blank=True,
        default=''
    )
    learned = models.TextField(
        _("""Did your character learn new skills or spells during game?  
        If so, list them here."""),
        blank=True,
        default=''
    )
    heavy_armor_worn_flag = models.BooleanField(
        _("Character wore heavy armor this event (cheaper Health pre-req)?"),
        default=False
    )
    what_did_you_do = HTMLField(
        _("What did you do during this event?"),
        blank=True, default=''
    )
    # taggit tags
    tags = TaggableManager()

    class Meta:
        """Ordering for grouping."""

        ordering = (
            "-event",
        )

    def __str__(self):
        return f"{self.character} | {self.event}"

    def get_absolute_url(self):
        """
        Get to the specific display for an instance.
        """
        return reverse('players:pel_detail', kwargs={'pk': self.pk})
