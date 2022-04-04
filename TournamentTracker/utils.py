import math
from .models import Player, TempPlayer, Tournament, School, Team, Match

def createTournamentFixture(teams):
    rows = math.ceil(len(teams)/2)
    columns = 0
    while(math.pow(2, columns) < rows): columns = columns + 1

    category = teams[0].category
    tournament = teams[0].tournament
    matchList = []

    matchNum = 1

    # loops through first column
    if len(teams) % 2 == 0:
        for i in range(0, len(teams), 2):
            try:
                match = Match.objects.filter(category = category, tournament = tournament, match_number = matchNum)[0]
            except:
                match = Match.objects.create(category = category, tournament = tournament, match_number = matchNum, team1 = teams[i], team2 = teams[i+1])
            matchList.append(match)
            matchNum = matchNum + 1
    else:
        for i in range(0, len(teams)-1, 2):
            try:
                match = Match.objects.filter(category = category, tournament = tournament, match_number = matchNum)[0]
            except:
                match = Match.objects.create(category = category, tournament = tournament, match_number = matchNum, team1 = teams[i], team2 = teams[i+1])            
            matchList.append(match)
            matchNum = matchNum + 1
        
        try:
            match = Match.objects.get(category = category, tournament = tournament, match_number = matchNum)
            if match.team1 != matchList[-1].winner:
                match.team1 = matchList[-1].winner
                match.save()
        except:
            match = Match.objects.create(category = category, tournament = tournament, match_number = matchNum, team1 = matchList[-1].winner, team2 = teams.last())
        matchNum = matchNum + 1

    currentRows = rows * math.pow(0.5, 1)
    counter = 1

    # loops through the rest of the columns
    while currentRows >= 1:
        futureMatches = []
        if currentRows % 2 == 0:
            for i in range(0, len(matchList), 2):
                try:
                    match = Match.objects.filter(category = category, tournament = tournament, match_number = matchNum)[0]
                    if match.team1 != matchList[i].winner or match.team2 != matchList[i+1].winner:
                        match.team1 = matchList[i].winner
                        match.team2 = matchList[i+1].winner
                        match.save()
                except:
                    match = Match.objects.create(category = category, tournament = tournament, team1 = matchList[i].winner, team2 = matchList[i+1].winner, match_number = matchNum)
                futureMatches.append(match)
                matchNum = matchNum + 1
        else:
            for i in range(0, len(matchList)-1, 2):
                try:
                    match = Match.objects.filter(category = category, tournament = tournament, match_number = matchNum)[0]
                    if match.team1 != matchList[i].winner or match.team2 != matchList[i+1].winner:
                        match.team1 = matchList[i].winner
                        match.team2 = matchList[i+1].winner
                        match.save()
                except:
                    match = Match.objects.create(category = category, tournament = tournament, team1 = matchList[i].winner, team2 = matchList[i+1].winner, match_number = matchNum)
                futureMatches.append(match)
                matchNum = matchNum + 1

            if currentRows != 1:
                try:
                    match = Match.objects.filter(category = category, tournament = tournament, match_number = matchNum)[0]
                    if match.team1 != futureMatches[-1].winner or match.team2 != matchList[-1].winner:
                        match.team1 = futureMatches[-1].winner
                        match.team2 = matchList[-1].winner
                        match.save()
                except:
                    match = Match.objects.create(category = category, tournament = tournament, team1 = matchList[i].winner, team2 = matchList[i+1].winner, match_number = matchNum)
                futureMatches.append(match)
                matchNum = matchNum + 1   

        counter = counter+1
        currentRows = math.floor(rows * math.pow(0.5, counter))
        matchList = futureMatches

def createModelDictList(objects):
    dictList = []
    for object in objects:
        for field in object._meta.fields:
            key = str(field).split(".")[-1]
            dictList.append({ key: object._meta.get_field(key) })

    return dictList

def getKeys(object):
    keyList = []
    for field in object._meta.fields:
        if str(field).endswith("id"):
            keyList.append("#")
        else:
            keyList.append(str(field).split(".")[-1]),

    return keyList


def on_match_won(winner, loser, score):
    tournament = Tournament.objects.get(id = winner.tournament.id)
    winner.wins = winner.wins + 1
    winner.save()

    winnerSchool = School.objects.get(id = winner.school.id)
    winnerSchool.points = winnerSchool.points + tournament.points_per_win
    # winnerSchool.wins = winnerSchool.wins + 1
    winnerSchool.save()


    loser.losses = loser.losses + 1
    loser.save()
    
    # loserSchool = School.objects.get(id = loser.school.id)
    # loserSchool.losses = loserSchool.losses + 1
    # loserSchool.save()
    createTournamentFixture(Team.objects.filter(tournament = tournament, category = winner.category))


def on_match_edited(winner, loser, score):
    tournament = Tournament.objects.get(id = winner.tournament.id)
    # adding and subtracting 2 to make up for the error victory and loss
    loser.wins = loser.wins - 2
    loser.save()

    winner.wins = winner.wins + 2
    winner.save()

    createTournamentFixture(Team.objects.filter(tournament = tournament, category = winner.category))


def on_start_tournament(tournamentId):
    tournament = Tournament.objects.get(id = tournamentId)
    createTournamentFixture(Team.objects.filter(tournament = tournament))

def create_teams(tournament, category):
    players = TempPlayer.objects.filter(tournament = tournament, category = category)
    for tempPlayer in players:
        try:
            team = Team.objects.get(
                tournament = tournament, 
                school = tempPlayer.school, 
                team_num = tempPlayer.team_num, 
                category = tempPlayer.category
            )
            
        except:
            team = Team.objects.create(
                tournament = tournament, 
                school = tempPlayer.school,
                team_num = tempPlayer.team_num, 
                category = tempPlayer.category
            )
        
        player = Player.objects.create(first_name = tempPlayer.first_name, last_name = tempPlayer.last_name)
        player.save()

        team.players.add(player)
        team.save()

        tempPlayer.delete()

def get_tournament_winner(tournament):
    winner = tournament.schools.all().order_by('-points')[0] # stores the school with the most points
    return winner

def saveMultiPlayerFormDetails(players, tournament, category):
    for player in players:
        playerData = player.split(",")
        school = tournament.schools.all().get(name = playerData[2].strip())
        tempPlayer = TempPlayer.objects.create(
            school = school, 
            tournament = tournament, 
            category = category, 
            first_name = playerData[0],
            last_name = playerData[1],
            team_num = playerData[3]
        )
        tempPlayer.save()


def createFixture(teams):
    matchArray = []
    firstIteration = False
    while (teams > 1):
        teams = (teams+1) >> 1
        matches = []

        for i in range(0, teams, 1):
            if teams % 2 == 1:
                if teams == 1:
                    matches.append([1])
                    continue
                
                if firstIteration:
                    matches.append(["odd1"])
                else:
                    matches.append(["odd!1"])
            else:
                if firstIteration:
                    matches.append(["even1"])
                else:
                    matches.append(["even!1"])
        firstIteration = False

        matchArray.append(matches)

    return matchArray