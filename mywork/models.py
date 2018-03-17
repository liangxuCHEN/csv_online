from django.db import models
from django.contrib.auth.models import User

import json
# Create your models here.


class TableModel(models.Model):
    table_name = models.CharField(max_length=256)
    created = models.DateTimeField(auto_now_add=True)

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
        return json.dumps(d)


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
        return json.dumps(d)