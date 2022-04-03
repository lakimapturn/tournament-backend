from django import forms
from django.forms import ModelForm
from django import forms

from .models import Match, Player, School, Sport, Team, TempPlayer, Tournament

class SchoolForm(ModelForm):
    class Meta:
        model = School
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'points': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(SchoolForm, self).__init__(*args, **kwargs)

class TournamentForm(ModelForm):
    class Meta:
        model = Tournament
        fields = ('name', 'sport', 'winner', 'start_date', 'end_date', 'categories', 'event_types', 'points_per_win')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sport': forms.Select(attrs={'class': 'form-control'}),
            'winner': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(),
            'end_date': forms.DateInput(),
            'categories': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'event_types': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'points_per_win': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(TournamentForm, self).__init__(*args, **kwargs)


class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = '__all__'
        widgets = {
            'tournament': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'school': forms.Select(attrs={'class': 'form-select'}),
            'wins': forms.NumberInput(attrs={'class': 'form-control'}),
            'losses': forms.NumberInput(attrs={'class': 'form-control'}),
            'draws': forms.NumberInput(attrs={'class': 'form-control'}),
            'players': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'team_num': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(TeamForm, self).__init__(*args, **kwargs)


class PlayerForm(ModelForm):
    class Meta:
        model = TempPlayer
        fields = '__all__'
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'team_num': forms.NumberInput(attrs={'class': 'form-control'}),
            'tournament': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'school': forms.Select(attrs={'class': 'form-select'}),
            'team_num': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'team_num': '<i>Change team number if 1 school has more than 1 team participating in the tournament</i>'
        }

    def __init__(self, *args, **kwargs):
        super(PlayerForm, self).__init__(*args, **kwargs)
        self.fields['team_num'].initial = 1


class MatchForm(ModelForm):
    class Meta:
        model = Match
        fields = ('category', 'team1', 'team2')
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'team1': forms.Select(attrs={'class': 'form-select'}),
            'team2': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super(MatchForm, self).__init__(*args, **kwargs)


class WinnerForm(ModelForm):
    class Meta:
        model = Match
        fields = ('winner', 'score')
        widgets = {
            'winner': forms.Select(attrs={'class': 'form-select'}),
            'score': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '<Team1 Score> - <Team2 Score>'}),
        }
        help_texts = {
            'score': 'Note: The order of score must correspond to the team number. <br /><i>Use the placeholder as an example</i>'
        }

    def __init__(self, *args, **kwargs):
        super(WinnerForm, self).__init__(*args, **kwargs)

