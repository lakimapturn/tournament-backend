from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, logout, login
from django.views import generic
from django.db.models import Q
from django import forms

import pandas as pd

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.views.decorators.csrf import csrf_exempt

from .forms import MatchExcelForm, PlayerExcelForm, MatchForm, MultiPlayerForm, MultiSchoolForm, PlayerForm, SchoolForm, TeamForm, TournamentForm, WinnerForm
from .models import Category, EventType, Match, Player, School, SchoolPoints, Team, Tournament
from .serializers import MatchSerializer, SchoolSerializer, TeamSerializer, TournamentDetailsSerializer, TournamentSerializer
from .utils import create_teams, get_tournament_winner, on_match_edited, on_match_won, createTournamentFixture, saveMultiPlayerFormDetails, savePlayerDetails

# Create your views here.


class TournamentListAPI(APIView):
    def get(self, request, *args, **kwargs):
        try:
            queryset = Tournament.objects.filter(~Q(status="Not Started"))
            serializer = TournamentSerializer(queryset, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TournamentDetailsAPI(APIView):
    def get(self, request, *args, **kwargs):
        try:
            queryset = Tournament.objects.get(id=request.query_params["id"])
            serializer = TournamentDetailsSerializer(queryset)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TeamDetailsAPI(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # add event type as well
            tournament = Tournament.objects.get(
                id=request.query_params['tournament_id'])
            event = EventType.objects.get(id=request.query_params['event_id'])
            category = Category.objects.get(
                gender=request.query_params['gender'],
                age=request.query_params['age'],
                event=event,
            )
            teams = Team.objects.filter(category=category, tournament=tournament).order_by(
                '-wins', '-draws', '-losses')

            serializer = TeamSerializer(teams, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SchoolAPI(APIView):
    def get(self, request, *args, **kwargs):
        try:
            queryset = School.objects.all()  # make it for a specific tournament
            serializer = SchoolSerializer(queryset, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except:
            print("error!")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MatchAPI(APIView):
    def get(self, request, *args, **kwargs):
        try:
            tournament = Tournament.objects.get(
                id=request.query_params['tournament_id'])
            event = EventType.objects.get(id=request.query_params['event_id'])
            category = Category.objects.get(
                gender=request.query_params['gender'],
                age=request.query_params['age'],
                event=event
            )
            teams = Team.objects.filter(
                tournament=tournament, category=category)
            queryset = Match.objects.filter(
                tournament=tournament, category=category)
            serializer = MatchSerializer(queryset, many=True)

            # createTournamentFixture(Team.objects.filter(tournament = Tournament.objects.get(id = 2)))
            return Response({'matches': serializer.data, 'initial-teams': teams.count()}, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def login_user(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))

            else:
                return render(request, 'Tournament/login.html', {
                    "message": 'Invalid Username/Password! Please Try Again!'
                })

        else:
            return render(request, 'Tournament/login.html')
    else:
        return HttpResponseRedirect(reverse('details_tournament'))


def logout_user(request):
    logout(request)
    return render(request, 'Tournament/login.html', {
        "message": "You Were Successfully Logged Out!"
    })


class TournamentEdit(generic.UpdateView):
    model = Tournament
    form_class = TournamentForm
    template_name = 'Tournament/form.html'
    success_url = reverse_lazy("details_tournament")
    extra_context = {'title': 'Edit Tournament',
                     'cancel_url': 'details_tournament'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tournament = Tournament.objects.get(id=self.kwargs["pk"])
        form = context["form"]
        # form.fields['categories'].queryset = tournament.categories
        form.fields['event_types'].queryset = tournament.event_types
        # form.fields['winner'].queryset = tournament.schools
        # ask sir if he would prefer having all options open when editing or narrowing the options down

        return context


class TournamentCreate(generic.CreateView):
    model = Tournament
    form_class = TournamentForm
    template_name = 'Tournament/form.html'
    extra_context = {'title': 'Create Tournament',
                     'cancel_url': 'details_tournament'}

    def post(self, request, *args, **kwargs) -> HttpResponse:
        form = TournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save()
            tournament.save()
        return HttpResponseRedirect(reverse_lazy("add_school", kwargs={'tournament_id': tournament.id}))


class TournamentList(generic.ListView):
    model = Tournament
    template_name = 'Tournament/details.html'
    paginate_by = 20
    extra_context = {
        'inner_template': "Tournament/details/tournaments.html",
        'title': 'Tournament',
        'add_url': 'add_tournament',
    }

    def get_queryset(self):
        print(self.kwargs)
        if self.kwargs != {}:
            return Tournament.objects.filter(id=self.kwargs['tournament_id'])
        return Tournament.objects.all()


class TournamentDetails(generic.DetailView):
    model = Tournament
    template_name = 'Tournament/tournament-details.html'
    extra_context = {'playerExcelForm': PlayerExcelForm,
                     'matchExcelForm': MatchExcelForm}


class SchoolEdit(generic.UpdateView):
    model = School
    form_class = SchoolForm
    template_name = 'Tournament/form.html'
    success_url = reverse_lazy("details_tournament")
    extra_context = {'title': 'Edit School'}


class SchoolCreate(generic.CreateView):
    model = SchoolForm
    form_class = SchoolForm
    template_name = 'Tournament/form.html'
    success_url = reverse_lazy("details_tournament")
    extra_context = {'title': 'Create School', 'success_url': 'add_player'}


class MultiSchoolCreate(generic.CreateView):
    model = School
    form_class = MultiSchoolForm
    template_name = 'Tournament/form.html'
    success_url = reverse_lazy("details_tournament")
    extra_context = {'title': 'Create School', 'success_url': 'add_player'}

    def post(self, request, *args, **kwargs) -> HttpResponse:
        form = MultiSchoolForm(request.POST)
        tournament = Tournament.objects.get(id=self.kwargs["tournament_id"])
        if form.is_valid():
            schools = form.cleaned_data["schools"].split("\n")

            for school_name in schools:
                school_name = school_name.strip()
                school = School.objects.get_or_create(name=school_name)[0]
                schoolPoints = SchoolPoints.objects.create(school=school)
                tournament.schools.add(schoolPoints)
            tournament.save()
        # reverse_lazy("add_player", kwargs = {'tournament_id': tournament.id})
        return HttpResponseRedirect(reverse_lazy("details_tournament", kwargs={'pk': tournament.id}))


class SchoolDetails(generic.ListView):
    model = School
    template_name = 'Tournament/details.html'
    paginate_by = 20
    extra_context = {
        'inner_template': "Tournament/details/schools.html",
        'title': 'School',
        'add_url': 'add_school',
    }


class TeamEdit(generic.UpdateView):
    model = Team
    form_class = TeamForm
    template_name = 'Tournament/form.html'
    success_url = reverse_lazy("details_team")
    extra_context = {'title': 'Edit Team', 'cancel_url': 'details_team'}


class TeamCreate(generic.CreateView):
    model = Team
    form_class = TeamForm
    template_name = 'Tournament/form.html'
    success_url = reverse_lazy("details_school")
    extra_context = {'title': 'Create Team', 'cancel_url': 'details_team'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        if self.kwargs:
            tournament = Tournament.objects.get(
                id=self.kwargs["tournament_id"])
            form.fields["tournament"].initial = tournament
            # context["form"].fields["tournament"].disabled = True
            form.fields["school"].queryset = tournament.schools
            form.fields["category"].queryset = tournament.categories

        return context


class TeamDetails(generic.ListView):
    model = Team
    template_name = 'Tournament/details.html'
    paginate_by = 20
    extra_context = {
        'inner_template': "Tournament/details/teams.html",
        'title': 'Team',
        'add_url': 'add_team',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs != {}:
            self.extra_context["add_url_parameter"] = self.kwargs['tournament_id']
        return context

    def get_queryset(self):
        print(self.kwargs)
        if self.kwargs != {}:
            return Team.objects.filter(tournament=self.kwargs['tournament_id'])
        return Team.objects.all()


class MatchEdit(generic.UpdateView):
    model = Match
    form_class = MatchForm
    template_name = 'Tournament/form.html'
    success_url = reverse_lazy("details_tournament")
    extra_context = {'title': 'Edit Match'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        if self.kwargs:
            match = Match.objects.get(id=self.kwargs["pk"])
            # function to filter teams that have either of the match team ids
            teams = Team.objects.filter(Q(id=match.team1.id) | Q(
                id=match.team2 and match.team2.id))
            form.fields["category"].queryset = Tournament.objects.get(
                id=match.tournament.id).categories
            if match.winner:
                form.fields["winner"].initial = match.winner
            else:
                form.fields["winner"].queryset = teams

        return context


class EditMatchWinner(generic.UpdateView):
    model = Match
    form_class = WinnerForm
    template_name = 'Tournament/form.html'
    success_url = reverse_lazy("details_tournament")
    extra_context = {
        'title': 'Edit Match Winner',
    }

    def form_valid(self, form):
        winner = form.cleaned_data['winner']
        match = Match.objects.get(id=self.kwargs["pk"])
        loser = match.team1.id == winner.id and match.team2 or match.team1

        on_match_edited(winner, loser)

        return super().form_valid(form)


class DeclareMatchWinner(generic.UpdateView):
    model = Match
    form_class = WinnerForm
    template_name = 'Tournament/form.html'
    success_url = reverse_lazy("details_tournament")
    extra_context = {
        'title': 'Declare Match Winner',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs:
            match = Match.objects.get(id=self.kwargs["pk"])
            self.success_url = reverse("details_match", kwargs={
                                       'tournament_id': match.tournament.id})
        return context

    def form_valid(self, form):
        winner = form.cleaned_data['winner']
        match = Match.objects.get(id=self.kwargs["pk"])
        loser = match.team1.id == winner.id and match.team2 or match.team1

        on_match_won(winner, loser)

        return super().form_valid(form)


class MatchDetails(generic.ListView):
    model = Match
    template_name = 'Tournament/details.html'
    paginate_by = 20
    extra_context = {
        'inner_template': "Tournament/details/matches.html",
        'title': 'Match',
    }

    def get_queryset(self):
        if self.kwargs != {}:
            tournament = self.kwargs['tournament_id']
            createMatchFixtures(self.request, tournament)
            return Match.objects.filter(tournament=tournament)
        return Match.objects.all()


class PlayerEdit(generic.UpdateView):
    model = Player
    form_class = PlayerForm
    template_name = 'Tournament/form.html'
    success_url = reverse_lazy("details_tournament")
    extra_context = {'title': 'Edit Player', 'cancel_url': 'details_player'}


class PlayerCreate(generic.CreateView):
    form_class = PlayerForm
    template_name = 'Tournament/form.html'
    success_url = reverse_lazy("details_tournament")
    extra_context = {'title': 'Create Player', 'cancel_url': 'details_player'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        form.fields["tournament"].queryset = Tournament.objects.filter(
            ~Q(status="Not Started"))
        if self.kwargs:
            tournament = Team.objects.get(id=self.kwargs["team_id"])
            form.fields["tournament"].initial = tournament

        return context


class MultiPlayerCreate(generic.CreateView):
    form_class = MultiPlayerForm
    template_name = 'Tournament/form.html'
    success_url = reverse_lazy("details_tournament")
    extra_context = {'title': 'Create Player', 'cancel_url': 'details_player'}

    def post(self, request, *args, **kwargs) -> HttpResponse:
        form = MultiPlayerForm(request.POST)

        if form.is_valid():
            tournament = Tournament.objects.get(
                id=form.cleaned_data['tournament'].id)
            category = Category.objects.get(
                id=form.cleaned_data['category'].id)
            data = form.cleaned_data['players']
            players = data.split("\n")
            saveMultiPlayerFormDetails(players, tournament, category)

            if self.kwargs:
                return HttpResponseRedirect(reverse_lazy("details_tournament", kwargs={'pk': self.kwargs["tournament_id"]}))
            return HttpResponseRedirect(reverse_lazy("add_player"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        if self.kwargs:
            tournament = Tournament.objects.get(
                id=self.kwargs["tournament_id"])
            form.fields["tournament"].initial = tournament

        return context


class PlayerDetails(generic.ListView):
    model = Player
    template_name = 'Tournament/details.html'
    paginate_by = 20
    extra_context = {
        'inner_template': "Tournament/details/players.html",
        'title': 'Players',
        'add_url': 'add_player',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs != {}:
            self.extra_context["add_url_parameter"] = self.kwargs['team_id']
        return context

    def get_queryset(self):
        if self.kwargs != {}:
            return Player.objects.filter(team=self.kwargs['team_id'])
        return Player.objects.all()


class Home(generic.TemplateView):
    template_name = "Tournament/home.html"
    extra_context = {
        "tournaments": Tournament.objects.all()
    }

    def get(self, request, *args, **kwargs):
        if self.kwargs != {}:
            self.extra_context["tournaments"] = Tournament.objects.filter(
                name__startswith=self.kwargs['search_query'])
        return super().get(request, *args, **kwargs)


def search(request):
    return HttpResponseRedirect(reverse("index", kwargs={'search_query': request.POST["search_query"]}))


def uploadPlayerList(request, tournament_id):
    if request.method == "POST":
        df = pd.read_excel(request.FILES["player_list"]).to_dict()
        savePlayerDetails(df, tournament_id, 1)

        # print(df)

    return HttpResponseRedirect(reverse("details_tournament", kwargs={'pk': tournament_id}))

# def uploadMatchList(request, tournament_id):
#     if request.method == "POST":
#         df = pd.read_excel(request.FILES["match_list"]).to_dict()

#         print(df)

#     return HttpResponseRedirect(reverse("details_tournament", kwargs={'pk': tournament_id}))


def createMatchFixtures(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    for category in tournament.categories.all():
        create_teams(tournament, category)
        createTournamentFixture(Team.objects.filter(
            tournament=tournament, category=category))

    return HttpResponseRedirect(reverse("details_tournament", kwargs={'pk': tournament_id}))


def start_tournament(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)

    tournament.status = "Ongoing"
    tournament.save()

    return HttpResponseRedirect(reverse("details_team"))


def end_tournament(request, tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
    tournament.status = "Ended"
    tournament.winner = get_tournament_winner(tournament)
    tournament.save()

    return HttpResponseRedirect(reverse("index"))


def returnToPrevPage(request):
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
