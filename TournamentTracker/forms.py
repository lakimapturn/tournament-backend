from django import forms
from django.db.models import Q

from .models import Match, Player, School, Team, TempPlayer, Tournament


class DateInput(forms.DateInput):
    input_type = 'date'
    attrs = {'class': 'form-control'}


class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(SchoolForm, self).__init__(*args, **kwargs)


class MultiSchoolForm(forms.ModelForm):
    schools = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        help_text='<i>Add every school on a new line</i>'
    )

    class Meta:
        model = School
        fields = ('schools',)
        # widgets = {
        #     'logo': forms.FileInput(attrs={'class': 'form-control'}),
        #     'points': forms.NumberInput(attrs={'class': 'form-control'}),
        # }

    def __init__(self, *args, **kwargs):
        super(MultiSchoolForm, self).__init__(*args, **kwargs)


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ('name', 'sport', 'start_date', 'end_date', 'cutoff_month',
                  'categories', 'event_types', 'points_per_win', 'image')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sport': forms.Select(attrs={'class': 'form-control'}),
            # 'winner': forms.Select(attrs={'class': 'form-control'}),
            'cutoff_month': forms.Select(attrs={'class': 'form-control'}),
            'start_date': DateInput(),
            'end_date': DateInput(),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'categories': forms.CheckboxSelectMultiple(attrs={'class': 'column-checkbox'}),
            'event_types': forms.CheckboxSelectMultiple(attrs={'class': 'column-checkbox'}),
            'points_per_win': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(TournamentForm, self).__init__(*args, **kwargs)


class TeamForm(forms.ModelForm):
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
            'players': forms.CheckboxSelectMultiple(attrs={'class': 'column-checkbox'}),
            'team_num': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(TeamForm, self).__init__(*args, **kwargs)


class TempPlayerForm(forms.ModelForm):
    class Meta:
        model = TempPlayer
        fields = '__all__'
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'tournament': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'school': forms.Select(attrs={'class': 'form-select'}),
            'team_num': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'team_num': '<i>Change team number if 1 school has more than 1 team participating in the tournament</i>'
        }

    def __init__(self, *args, **kwargs):
        super(TempPlayerForm, self).__init__(*args, **kwargs)
        self.fields['team_num'].initial = 1


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = '__all__'
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class MultiPlayerForm(forms.ModelForm):
    players = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'First_name, Last_name, School, Team_number'
        }),
        help_text='<i>Add every player on a new line</i><br /><i>Follow this format: First_name, Last_name, School Team_number</i><br /><i>Ensure that the school name entered corresponds to the name entered previously</i>',
    )

    class Meta:
        model = TempPlayer
        fields = ('tournament', 'category', 'players')
        widgets = {
            'tournament': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super(MultiPlayerForm, self).__init__(*args, **kwargs)


class MatchForm(forms.ModelForm):
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


class WinnerForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ('winner',)
        widgets = {
            'winner': forms.Select(attrs={'class': 'form-select'}),
            # 'score': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '<Team1 Score> - <Team2 Score>'}),
        }
        help_texts = {
            'score': 'Note: The order of score must correspond to the team number. <br /><i>Use the placeholder as an example</i>'
        }

    def __init__(self, *args, **kwargs):
        super(WinnerForm, self).__init__(*args, **kwargs)
        match = kwargs['instance']
        teams = Team.objects.filter(Q(id=match.team1.id) | Q(
            id=match.team2 and match.team2.id))
        self.fields["winner"].queryset = teams

        if match.score is not None:
            scores = match.score.split("/")[1:-1]

        for i in range(match.tournament.sets):
            setScore = "0-0"
            if scores and i < len(scores):
                setScore = scores[i]

            self.fields[f"set {i+1} score"] = forms.CharField(
                widget=forms.TextInput(attrs={'class': 'form-control'}), initial=setScore)

    def save(self, *args, **kwargs):
        score = ""
        team1Wins = 0
        team2Wins = 0

        i = 1
        while True:
            setScore: str = self[f'set {i} score'].data

            if setScore == "0-0":
                print("Empty Set!")
                break

            team1Score = int(setScore[:setScore.index("-")])
            team2Score = int(setScore[setScore.index("-")+1:])

            if team1Score > team2Score:
                team1Wins += 1
            else:
                team2Wins += 1

            score += setScore+"/"

            i += 1

        score = f"{team1Wins}-{team2Wins}/" + score

        self.score = score
        return super().save(*args, **kwargs)


class PlayerExcelForm(forms.Form):
    player_list = forms.FileField(widget=forms.FileInput(attrs={
        'class': 'form-control',
    }))

    def __init__(self, *args, **kwargs):
        super(PlayerExcelForm, self).__init__(*args, **kwargs)
        self.fields['player_list'].label = "Upload the Player List Here:"


class MatchExcelForm(forms.Form):
    match_list = forms.FileField(widget=forms.FileInput(attrs={
        'class': 'form-control',
    }))

    def __init__(self, *args, **kwargs):
        super(MatchExcelForm, self).__init__(*args, **kwargs)
        self.fields['match_list'].label = "Upload the Match List Here:"
