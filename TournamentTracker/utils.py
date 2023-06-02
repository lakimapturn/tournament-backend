from datetime import date
import math
import pandas as pd
from .models import Category, Player, SchoolPoints, TempPlayer, Tournament, School, Team, Match, EventType


def add_match_players(team1, team2, match):
    team1Players = team1 and team1.players.all().distinct() or None
    team2Players = team2 and team2.players.all().distinct() or None
    if not (team1Players and team2Players):
        return

    length = len(team1Players and team1Players or team2Players)
    for j in range(0, length):
        if team1Players and team1Players[j].role == 'Starting':
            match.played_by.add(team1Players[j])
        if team2Players and team2Players[j].role == 'Starting':
            match.played_by.add(team2Players[j])


def createTournamentFixture(teams) -> None:
    if (len(teams) == 0):
        return

    rows = math.ceil(len(teams)/2)
    columns = 0
    while (math.pow(2, columns) < rows):
        columns = columns + 1

    category = teams[0].category
    tournament = teams[0].tournament
    matchList = []

    matchNum = 1

    # loops through first column
    if len(teams) % 2 == 0:
        for i in range(0, len(teams), 2):
            match = updateMatch(tournament, category,
                                matchNum, teams[i], teams[i+1])

            matchList.append(match)
            matchNum = matchNum + 1
    else:
        for i in range(0, len(teams)-1, 2):
            match = updateMatch(tournament, category,
                                matchNum, teams[i], teams[i+1])

            matchList.append(match)
            matchNum = matchNum + 1
        # matchList.pop()

        match = updateMatch(tournament, category, matchNum,
                            matchList[-1].winner, teams.last())

        matchList.append(match)
        matchNum += 1

    currentRows = math.floor(rows * math.pow(0.5, 1))
    colCounter = 1

    # loops through the rest of the columns
    while currentRows >= 1:
        futureMatches = []
        if currentRows % 2 == 0:
            # why does len have to be matchList-1 ????
            for i in range(0, len(matchList), 2):
                match = updateMatch(
                    tournament, category, matchNum, matchList[i].winner, matchList[i+1].winner)

                futureMatches.append(match)
                matchNum += 1
        else:
            if currentRows == 1:
                loser1 = matchList[0].winner == matchList[0].team1 and matchList[0].team2 or matchList[0].team1
                loser2 = matchList[1].winner == matchList[1].team1 and matchList[1].team2 or matchList[1].team1

                updateMatch(tournament, category, matchNum, loser1, loser2)

                matchNum += 1

            for i in range(0, len(matchList)-1, 2):
                match = updateMatch(
                    tournament, category, matchNum, matchList[i].winner, matchList[i+1].winner)

                futureMatches.append(match)
                matchNum += 1

            """ 
            In the case of 2 matches happening in first round, matchList has 2 matches. 
            It adds the final match to the future matches and then doesnt run anymore which is perfect.
            Behaviour with more matches may be different.
            The next if statement shouldnt run because in the case of 1 match left, that match has already been added
            """

            if currentRows > 1:
                # matchList.pop()  # check if necessary

                match = updateMatch(
                    tournament, category, matchNum, futureMatches[-1].winner, matchList[-1].winner)

                futureMatches.append(match)
                matchNum = matchNum + 1

        colCounter = colCounter+1
        currentRows = math.floor(rows * math.pow(0.5, colCounter))
        matchList = futureMatches


def updateMatch(tournament, category, matchNum, team1, team2):
    match, created = Match.objects.get_or_create(
        category=category, tournament=tournament, match_number=matchNum)
    if match.team1 != team1 or match.team2 != team2:
        match.team1 = team1
        match.team2 = team2
        match.save()

    if created:
        match.team1 = team1
        match.team2 = team2
        add_match_players(
            team1, team2, match
        )
        match.save()

    return match


def on_match_changed(winner, loser, edited):
    tournament = winner.tournament
    pointsPerWin = tournament.points_per_win
    winnerSchool = tournament.schools.get(school=winner.school.id)
    loserSchool = tournament.schools.get(school=loser.school.id)

    # adding and subtracting to make up for the error victory and loss
    loser.losses = loser.losses + 1
    loser.save()

    winner.wins = winner.wins + 1
    winnerSchool.points += pointsPerWin
    winner.save()

    if (edited):
        loser.wins = max(loser.wins - 1, 0)
        winner.losses = max(loser.wins - 1, 0)
        loserSchool.points = max(loserSchool.points - pointsPerWin, 0)

    createTournamentFixture(Team.objects.filter(
        tournament=tournament, category=winner.category))


def on_start_tournament(tournamentId):
    tournament = Tournament.objects.get(id=tournamentId)
    createTournamentFixture(Team.objects.filter(tournament=tournament))


def create_teams(tournament, category):
    players = TempPlayer.objects.filter(
        tournament=tournament, category=category)
    for tempPlayer in players:
        try:
            team = Team.objects.get(
                tournament=tournament,
                school=tempPlayer.school,
                team_num=tempPlayer.team_num,
                category=tempPlayer.category
            )

        except:
            team = Team.objects.create(
                tournament=tournament,
                school=tempPlayer.school,
                team_num=tempPlayer.team_num,
                category=tempPlayer.category
            )

        player = Player.objects.create(
            first_name=tempPlayer.first_name, last_name=tempPlayer.last_name, role=tempPlayer.role)
        player.save()

        team.players.add(player)
        team.save()

        tempPlayer.delete()


def get_tournament_winner(tournament):
    # stores the school with the most points
    winner = tournament.schools.all().order_by('-points')[0]
    return winner.school


def saveMultiPlayerFormDetails(players, tournament, category):
    for player in players:
        playerData = player.split(",")
        school = School.objects.get(name=playerData[2].strip())
        tempPlayer = TempPlayer.objects.create(
            school=school,
            tournament=tournament,
            category=category,
            first_name=playerData[0],
            last_name=playerData[1],
            team_num=playerData[3]
        )
        tempPlayer.save()


# def createFixture(teams):
#     matchArray = []
#     firstIteration = False
#     while (teams > 1):
#         teams = (teams+1) >> 1
#         matches = []

#         for i in range(0, teams, 1):
#             if teams % 2 == 1:
#                 if teams == 1:
#                     matches.append([1])
#                     continue

#                 if firstIteration:
#                     matches.append(["odd1"])
#                 else:
#                     matches.append(["odd!1"])
#             else:
#                 if firstIteration:
#                     matches.append(["even1"])
#                 else:
#                     matches.append(["even!1"])
#         firstIteration = False

#         matchArray.append(matches)

#     return matchArray

months = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12
}


def formatDate(dateStr) -> date:
    dateStr = str(dateStr)
    d = dateStr.split("-")
    return date(int(d[0]), int(d[1]), int(d[2].split(" ", 1)[0]))


def getCategory(dob, gender, event, tournament: Tournament) -> Category:
    dob = formatDate(dob)
    age = date.today().year - dob.year

    cutoffMonth = tournament.cutoff_month

    for category in tournament.categories.filter(age__gte=age, gender=gender, event=event).order_by('age'):
        if category.age > age or (category.age == age and months[cutoffMonth] <= dob.month):
            return category


def savePlayerDetails(df, tournament_id, category_id):
    if df['fullname']:
        tournament = Tournament.objects.get(id=tournament_id)

        length = len(df['fullname'])
        data = {}

        for i in range(length):
            category = getCategory(
                df['dob'][i], df['gender'][i], EventType.objects.get(name=df['event'][i]), tournament)

            if category == None:
                continue

            name = df['fullname'][i].split(" ")
            school = School.objects.get(name=df['school'][i].strip())

            player = TempPlayer.objects.get_or_create(
                tournament=tournament,
                category=category,
                first_name=name[0],
                last_name=name[1],
                school=school,
                team_num=df['team_number'][i],
                role=df['role'][i],
            )
            player[0].save()
            data[i] = {"first_name": name[0], "last_name": name[1],
                       "school": df['school'][i], "team_number": df['team_number'][i]}

        print(data)
        return data
    else:
        return {}
