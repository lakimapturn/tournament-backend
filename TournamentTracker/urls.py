from django.urls import path
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static 

from . import views

urlpatterns = [
    path('', login_required(views.Home.as_view()), name='index'),
    path('search', login_required(views.search), name='search'),
    path('search/<str:search_query>', login_required(views.Home.as_view()), name='index'),
    
    path('tournament-list', views.TournamentListAPI.as_view()),
    path('tournament-details', views.TournamentDetailsAPI.as_view()),
    path('teams', views.TeamDetailsAPI.as_view()),
    path('schools', views.SchoolAPI.as_view()),
    path('matches', views.MatchAPI.as_view()),

    path('tournament/add', login_required(views.TournamentCreate.as_view()), name="add_tournament"),
    path('tournament/edit/<int:pk>', login_required(views.TournamentEdit.as_view()), name="edit_tournament"),
    path('tournament/details', login_required(views.TournamentList.as_view()), name="details_tournament"),
    path('tournament/details/<int:pk>', login_required(views.TournamentDetails.as_view()), name="details_tournament"),

    path('school/add', login_required(views.SchoolCreate.as_view()), name="add_school"),
    path('school/add/<int:tournament_id>', login_required(views.MultiSchoolCreate.as_view()), name="add_school"),
    path('school/edit/<int:pk>', login_required(views.SchoolEdit.as_view()), name="edit_school"),
    path('school/details', login_required(views.SchoolDetails.as_view()), name="details_school"),

    path('team/add/<int:tournament_id>', login_required(views.TeamCreate.as_view()), name="add_team"),
    path('team/add', login_required(views.TeamCreate.as_view()), name="add_team"),
    path('team/<int:pk>', login_required(views.TeamEdit.as_view()), name="edit_team"),
    path('team/details/<int:tournament_id>', login_required(views.TeamDetails.as_view()), name="details_team"),
    path('team/details', login_required(views.TeamDetails.as_view()), name="details_team"),

    path('player/add', login_required(views.PlayerCreate.as_view()), name="add_player"),
    path('player/add/<int:tournament_id>', login_required(views.MultiPlayerCreate.as_view()), name="add_player"),
    path('player/<int:pk>', login_required(views.PlayerEdit.as_view()), name="edit_player"),
    path('player/details/<int:team_id>', login_required(views.PlayerDetails.as_view()), name="details_player"),
    path('player/details', login_required(views.PlayerDetails.as_view()), name="details_player"),

    path('match/details/<int:tournament_id>', login_required(views.MatchDetails.as_view()), name="details_match"),
    path('match/edit/<int:pk>', login_required(views.MatchEdit.as_view()), name="edit_match"),
    path('match/winner/<int:pk>', login_required(views.DeclareMatchWinner.as_view()), name="declare_match_winner"),
    path('match/edit-winner/<int:pk>', login_required(views.EditMatchWinner.as_view()), name="edit_match_winner"),

    path('login', views.login_user, name="login"),
    path('logout', views.logout_user, name="logout"),

    path('start-tournament/<int:tournament_id>', views.start_tournament, name="start_tournament"),
    path('end-tournament/<int:tournament_id>', views.end_tournament, name="end_tournament"),
    path('add-another', views.returnToPrevPage, name="add_another"),

    path('upload-player-list/<int:tournament_id>', views.uploadPlayerList, name="upload_player_list"),
    # path('upload-match-list/<int:tournament_id>', views.uploadMatchList, name="upload_match_list"),
    path('create-matches/<int:tournament_id>', views.createMatchFixtures, name="create_matches"),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
# urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)