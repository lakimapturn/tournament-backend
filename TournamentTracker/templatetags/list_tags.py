import os
from django import template
import pandas as pd
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings

from ..models import Category, Team, Tournament

register = template.Library()


@register.simple_tag
def index(dict, key):
    return dict[key]


@register.simple_tag
def player_count(tournamentId):
    count = 0
    tournament = Tournament.objects.get(id=tournamentId)
    for team in Team.objects.filter(tournament=tournament):
        count = count + team.players.count()

    return count


@register.simple_tag
def replaceStr(str, str1, str2):
    return str.replace(str1, str2)


@register.simple_tag
def getValidatedTemplate(tournament: Tournament):
    templateUrl = finders.find('excel/template.xlsx')
    writtenUrl = finders.find('excel/players_list.xlsx')

    template = pd.ExcelFile(templateUrl)
    df = pd.read_excel(template)

    df.to_excel(writtenUrl, engine='xlsxwriter')

    writer = pd.ExcelWriter(writtenUrl, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')

    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

# Adding Data Validation
    tournamentSchools = tournament.schools.all()
    worksheet.data_validation('C2:C400', {'validate': 'list',
                                          'source': [school.school.name for school in tournamentSchools]})

    worksheet.data_validation('F2:F400', {'validate': 'list',
                                          'source': ["Male", "Female"]})

    worksheet.data_validation('G2:G400', {'validate': 'list',
                                          'source': ["Starting", "Substitute"]})

    tournamentEvents = tournament.event_types.all()
    worksheet.data_validation('H2:H400', {'validate': 'list',
                                          'source': [event.name for event in tournamentEvents]})
    writer.save()

    return staticfiles_storage.url('excel/players_list.xlsx')
