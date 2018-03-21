from django.db import models
from django.contrib.auth.models import User

import uuid

# Create your models here.

class UUIDTools(object):
    """uuid function tools"""

    @staticmethod
    def uuid1_hex():
        """
        return uuid1 hex string
        eg: 23f87b528d0f11e696a7f45c89a84eed
        """
        return uuid.uuid1().hex


class TableModel(models.Model):
    table_name = models.CharField(max_length=256)
    created = models.DateTimeField(auto_now_add=True)
    table_url = models.CharField(max_length=40, default=UUIDTools.uuid1_hex, editable=False)

    class Meta:
        ordering = ('created',)

    def __unicode__(self):
        return '%s' % self.table_name

    def __str__(self):
        return '%s' % self.table_name

    def to_json(self):
        d = {}
        for field in self._meta.fields:
            d[field.name] = getattr(self, field.name)

        d['created'] = d['created'].strftime('%Y-%m-%d %H:%M:%S')
        return d


class AuthTableModel(models.Model):
    users = models.ManyToManyField(User)
    table = models.OneToOneField(TableModel, on_delete=models.CASCADE)
    detail_auth = models.CharField(max_length=256, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s' % self.table.table_name

    def __str__(self):
        return '%s' % self.table.table_name

    def to_json(self):
        d = {}
        for field in self._meta.fields:
            d[field.name] = getattr(self, field.name)

        d['created'] = d['created'].strftime('%Y-%m-%d %H:%M:%S')
        return d


class TableMessageModel(models.Model):
    table = models.ForeignKey(TableModel, on_delete=models.CASCADE, editable=False)
    user =  models.CharField(max_length=128)
    user_id = models.CharField(max_length=10)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)

    def __unicode__(self):
        return '%s' % self.table.table_name

    def to_json(self):
        d = {}
        for field in self._meta.fields:
            d[field.name] = getattr(self, field.name)

        d['table'] = d['table'].table_name
        d['created'] = d['created'].strftime('%Y-%m-%d %H:%M:%S')

        return d




