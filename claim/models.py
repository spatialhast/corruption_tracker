# -*- coding: utf-8 -*-
import datetime
import json

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from multiselectfield import MultiSelectField


STATUSES = (('not_moderated', _('Not moderated')),
            ('suspicious', _('Suspicious')),
            ('anonymous', _('From anonymous')),
            ('valid', _('Moderated')),
            ('markers', _('Non-verified markers'))
            )


class Moderator(models.Model):
    """
    Singleton model, where admin can choose
    claims with wich state of moderation to show

    """

    show_claims = MultiSelectField(choices=STATUSES, max_length=200,
        default='not_moderated,suspicious,anonymous,valid')

    # memcached settings
    use_memcached = models.BooleanField(default=False)
    memcached_timeout = models.IntegerField(default=3600)
    claims_per_hour = models.IntegerField(default=3)

    class Meta:
        verbose_name_plural = "Moderator"

    def save(self, *args, **kwargs):
        self.id = 1
        super(Moderator, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass


class OrganizationType(models.Model):
    type_id = models.CharField(primary_key=True, max_length=155)
    name = models.CharField(max_length=255)


    def claim_types(self):
        claim_types = self.claimtype_set.all()
        claim_types_list = []

        for claim_type in claim_types:
            claim_types_list.append({
                'id': claim_type.id,
                'name':claim_type.name,               
                'icon': claim_type.icon.url if\
                    claim_type.icon else False
                })
        return claim_types_list



    def __str__(self):
        return self.type_id


class ClaimType(models.Model):
    """
    Binding the set of ClaimType objects to OrganizationType
    allow to show to user dropdown with common violations
    in organizations of certain type

    """
    name = models.CharField(max_length=555)
    org_type = models.ManyToManyField(OrganizationType)
    icon = models.FileField(upload_to='icons/', null=True, blank=True)

    def __str__(self):
        return self.name

    def linked_org_types(self):
        return ','.join([x.type_id for x in self.org_type.all()])


class Organization(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(null=True, blank=True)
    org_type = models.ForeignKey(OrganizationType, null=True, blank=True)

    updated = models.DateTimeField(auto_now=True)

    def moderation_filter(self):
        allowed_statuses = Moderator.objects.get(id=1).show_claims
        return self.claim_set.filter(moderation__in=allowed_statuses)

    def first_polygon(self):
        try:
            return self.polygon_set.all()[0]
        except IndexError:
            return None

    @property
    def total_claims(self):
        return self.moderation_filter().count()


    # def claim_types(self):
    #     claim_types = ClaimType.objects.filter(org_type=self.org_type)
    #     claim_types_list = []

    #     for claim_type in claim_types:
    #         claim_types_list.append({
    #             'id': claim_type.id,
    #             'name':claim_type.name,               
    #             'icon': claim_type.icon.url if\
    #                 claim_type.icon else False
    #             })
    #     return claim_types_list

    def json_claims(self, limit=999):
        claims = self.moderation_filter()

        claims_list = []

        if claims:
            for claim in claims:
                claim_type = claim.claim_type.name if\
                    claim.claim_type else _('Others')
                claim_icon = claim.claim_type.icon.url if\
                    claim.claim_type.icon else False
                username = claim.complainer.username if\
                    claim.complainer else _("Anon")
                bribe = claim.bribe if claim.bribe else 0
                claims_list.append({
                    'organization_id': self.id,
                    'organization_name': self.name,
                    'text': claim.text,
                    'servant': claim.servant,
                    'complainer': username,
                    'claim_type': claim_type,
                    'created': claim.created.strftime('%Y-%m-%d %H:%M:%S'),
                    'claim_icon': claim_icon,
                    'bribe': bribe
                })

        return claims_list[:limit]

    def __str__(self):
        return self.name


class InCharge(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)

    organizations = models.ManyToManyField(Organization)
    organization_types = models.ManyToManyField(OrganizationType)

    def __str__(self):
        return self.name


class Claim(models.Model):
    text = models.CharField(max_length=2550)
    created = models.DateTimeField(default=datetime.datetime.now)
    live = models.BooleanField(default=False)
    organization = models.ForeignKey(Organization)
    servant = models.CharField(max_length=550)
    complainer = models.ForeignKey(User, null=True, blank=True, default=None)
    claim_type = models.ForeignKey(ClaimType, null=True, blank=True,
                                   default=None)
    # moderation = models.ForeignKey(ModerationStatus, default='not_moderated')
    moderation = models.CharField(choices=STATUSES, max_length=50,
                                  default='not_moderated')
    bribe = models.IntegerField(blank=True, null=True)
