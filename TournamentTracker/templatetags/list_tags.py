from django import template

from ..models import Team, Tournament

register = template.Library()

@register.simple_tag
def index(dict, key):   
    return dict[key]

@register.simple_tag
def player_count(tournamentId):
    count = 0
    tournament = Tournament.objects.get(id = tournamentId)
    for team in Team.objects.filter(tournament = tournament):
        count = count + team.players.count()
    
    return count

@register.simple_tag
def replaceStr(str, str1, str2):
    return str.replace(str1, str2)