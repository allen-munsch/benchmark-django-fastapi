from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Location(models.Model):
    line_1 = models.CharField(blank=True, default="", max_length=50)
    line_2 = models.CharField(blank=True, default="", max_length=50)
    line_3 = models.CharField(blank=True, default="", max_length=50)
    zipcode = models.CharField(blank=True, default="", max_length=50)

class PerformerMixin(User):
    stage_name = models.CharField(blank=True, null=True, max_length=50)

class Clown(PerformerMixin):
    CHOICES = (
        ('CIRCUS_ARTS', 'Circus Arts'),
        ('MIME', 'Mime'),
        ('DANCE', 'Dance'),
        ('PHSYCIAL_COMEDY', 'Physical Comedy'),
        ('DEVISING', 'Devising'),
        ('DIRECT_AUDIENCE_RELATIONSHIP', 'Direct Audience Relationship'),
        ('OBJECT_MANIPULATION_PROPS_SETS', 'Object Manipulation Props and Sets'),
        ('CLOWN_DRAMATURGY', 'Clown Dramaturgy'),
    )
    concentration = models.CharField(choices=CHOICES, max_length=50)

class Acrobat(PerformerMixin):
    CHOICES = (
        ('HAND_BALANCING', 'Hand balancing'),
        ('TUMBLING', 'Tumbling'),
        ('JUGGLING', 'Juggling'),
        ('PARTNER_ACRO', 'Partner acro'),
        ('CONTORTION', 'Contortion'),
        ('TIGHTWIRE', 'Tightwire'),
        ('STILT_WALKING', 'Stilt walking'),
        ('ROLLING_GLOBE', 'Rolling globe'),
        ('AERIAL_SKILLS', 'Aerial skills'),
        ('STATIC/DANCE_TRAPEZE', 'Static/dance trapeze'),
        ('SILKS', 'Silks'),
        ('LYRA', 'Lyra'),
        ('STRAPS', 'Straps'),
        ('SPANISH_WEB_CORDE_LISSE', 'Spanish web/corde lisse'),
        ('CHINESE_POLE', 'Chinese pole'),
        ('ACROBATIC_SAFETY_AND_RIGGING_INSTRUCTION', 'Acrobatic safety and rigging instruction'),
    )
    concentration = models.CharField(choices=CHOICES, max_length=50)

class Troupe(models.Model):
    name = models.CharField(blank=True, null=True, default="", max_length=50)
    clowns = models.ManyToManyField(Clown)
    acrobats = models.ManyToManyField(Acrobat)

class ClownCollege(models.Model):
    name = models.CharField(default="Clown University", max_length=50)
    location = models.ForeignKey(Location, related_name="circus", on_delete=models.CASCADE)
    troupe = models.ForeignKey(Troupe, related_name="circus", on_delete=models.CASCADE)

