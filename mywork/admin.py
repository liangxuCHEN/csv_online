from django.contrib import admin
from mywork.models import TableModel,AuthTableModel, TableMessageModel
# Register your models here.

class TableModelAdmin(admin.ModelAdmin):
    list_display = ('table_name', 'table_url','created')


class AuthTableModelAdmin(admin.ModelAdmin):
    list_display = ('table', 'created')


class TableMessageModelAdmin(admin.ModelAdmin):
    list_display = ('table', 'created')

admin.site.register(TableModel, TableModelAdmin)
admin.site.register(AuthTableModel, AuthTableModelAdmin)
admin.site.register(TableMessageModel, TableMessageModelAdmin)
