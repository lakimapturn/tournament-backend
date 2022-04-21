from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

playerRoles = (('Starting', 'Starting'), ('Substitute', 'Substitute'))

class User(AbstractUser):
    def __str__(self):
        return self.username

    class Meta:
        	ordering = ('first_name', 'last_name')

class Sport(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, default="")
    image = models.ImageField(null=True, blank=True, default="")

    def __str__(self):
        return self.name

    class Meta:
        	ordering = ('name',)

class School(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, default="")
    logo = models.ImageField(null=True, blank=True, default="")

    def __str__(self):
        return self.name

    class Meta:
        	ordering = ('name', )

class SchoolPoints(models.Model):
    school = models.ForeignKey(School, on_delete = models.CASCADE, blank = False, null=False)
    points = models.PositiveIntegerField(null=False, blank=False, default=0)

    def __str__(self):
        return self.school.name

    class Meta:
        	ordering = ('points', )

class EventType(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, default="")
    image = models.ImageField(null=True, blank=True, default="")

    def __str__(self):
        return self.name

    class Meta:
        	ordering = ('name',)

class Category(models.Model):
    gender_choices = (('Female', 'Female'), ('Male', 'Male'))

    age = models.PositiveIntegerField(default=0, null=False, blank=False)
    gender = models.CharField(max_length=6, default="", choices=gender_choices, null=False, blank=False)
    event = models.ForeignKey(EventType, on_delete=models.CASCADE, blank = True, null=True)

    def __str__(self):
        return "U" + str(self.age) + " - " + self.gender + " ( " + self.event.name + " )"

class Tournament(models.Model):
    STATUS = (('Not Started', 'Not Started'), ('Ongoing', 'Ongoing'), ('Ended', 'Ended'))

    name = models.CharField(max_length=255, null=False, blank=False, default="")
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, null=False, blank=False)
    winner = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    categories = models.ManyToManyField(Category, related_name="category_tournaments", blank=False)
    event_types = models.ManyToManyField(EventType, related_name="event_tournaments", blank = False)
    schools = models.ManyToManyField(SchoolPoints, related_name="tournaments", blank = True)
    status = models.CharField(max_length=16, choices=STATUS, default='Not Started', null=True, blank=True)
    points_per_win = models.PositiveSmallIntegerField(default=1, null=True, blank=True)
    image = models.ImageField(null=True, blank=True, default="")
    # player_list = models.FileField(null=True, blank=True, default=None)

    def __str__(self):
        return self.name

    class Meta:
        	ordering = ('name',)

class Player(models.Model):
    first_name = models.CharField(max_length=100, null=False, blank=False, default="")
    last_name = models.CharField(max_length=100, null=False, blank=False, default="")
    role = models.CharField(max_length=10, choices=playerRoles ,null=False, blank=False, default="")
    # add age attribute?

    def __str__(self):
        return self.first_name + " " + self.last_name

class Team(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=False, blank=False, default="", related_name="tournament_teams")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False, blank=False, default="")
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=False, blank=False)
    wins = models.PositiveIntegerField(null=False, blank=False, default=0)
    draws = models.PositiveIntegerField(null=False, blank=False, default=0)
    losses = models.PositiveIntegerField(null=False, blank=False, default=0)
    players = models.ManyToManyField(Player, blank=False, related_name="team")
    team_num = models.PositiveSmallIntegerField(null=False, blank=False, default=1)

    def __str__(self):
        return self.tournament.name + " " + self.school.name + ": " + "U" + str(self.category.age) + " - " + self.category.gender + " ( " + self.category.event.name + " )  Team " + str(self.team_num)

class TempPlayer(models.Model):
    first_name = models.CharField(max_length=100, null=False, blank=False, default="")
    last_name = models.CharField(max_length=100, null=False, blank=False, default="")
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=False, blank=False, default="", related_name="temp_players")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False, blank=False, default="")
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=False, blank=False)
    team_num = models.PositiveSmallIntegerField(null=False, blank=False, default=0)
    role = models.CharField(max_length=10, choices=playerRoles ,null=False, blank=False, default="")

    def __str__(self):
        return self.first_name + " " + self.last_name

class Match(models.Model):
    contestants = (('Team1', 'Team1'), ('Team2', 'Team2'))

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=False, blank=False, related_name="tournament_matches")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False, blank=False, related_name="category_matches")
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, blank = True, null=True, related_name="team1_match")
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, blank = True, null=True, related_name="team2_match")
    winner = models.ForeignKey(Team, on_delete=models.CASCADE, blank = True, null=True,related_name="match_winner")
    score = models.CharField(max_length=32, default="", null=True, blank=True)
    match_number = models.PositiveSmallIntegerField(null=False, blank=False, default=1)
    played_by = models.ManyToManyField(Player, blank=True, related_name="matches_played")

    def __str__(self):
        return self.tournament.name + " - Match" + str(self.match_number) + " ( " + self.category.event.name + " )"


# IF AN ERROR COMES SAYING A COLUMN DOESNT EXIST... ITS CAUSE OF THE GENERIC DETAIL VIEWS IN views.py