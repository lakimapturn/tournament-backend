from django.contrib import admin

from .models import Category, Match, Player, School, SchoolPoints, Sport, Team, TempPlayer, Tournament, User, EventType
# Register your models here.

admin.site.register(User)
admin.site.register(Sport)
admin.site.register(School)
admin.site.register(SchoolPoints)
admin.site.register(EventType)
admin.site.register(Tournament)
admin.site.register(Category)
admin.site.register(Match)
admin.site.register(Player)
admin.site.register(TempPlayer)
admin.site.register(Team)
