from django.contrib import admin
from .models import *
from simple_history.admin import SimpleHistoryAdmin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(Gara)
admin.site.register(Squadra)
admin.site.register(Evento, SimpleHistoryAdmin)
admin.site.register(Consegna, SimpleHistoryAdmin)
admin.site.register(Jolly)
admin.site.register(Soluzione)

class MyUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'gender', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informazioni personali', {'fields': ('first_name', 'last_name', 'email', 'gender')}),
        ('Permessi', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Date importanti', {'fields': ('last_login', 'date_joined')}))

admin.site.register(User, MyUserAdmin)
