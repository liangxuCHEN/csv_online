from django.contrib import admin
from mywork.models import TableModel,AuthTableModel
# Register your models here.

class TableModelAdmin(admin.ModelAdmin):
    list_display = ('table_name', 'created')


class AuthTableModelAdmin(admin.ModelAdmin):
    list_display = ('table', 'created')

admin.site.register(TableModel, TableModelAdmin)
admin.site.register(AuthTableModel, AuthTableModelAdmin)

