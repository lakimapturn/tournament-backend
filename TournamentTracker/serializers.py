from rest_framework import serializers

from .models import Category, Match, Player, School, SchoolPoints, Team, Tournament


class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = (
            'id', 'name', 'sport', 'start_date', 'end_date', 'event_types', 'status', 'image'
        )

        depth = 1


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = (
            'id', 'first_name', 'last_name'
        )

        depth = 2


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = (
            'id', 'name', 'logo'
        )


class SchoolPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolPoints
        fields = (
            'id', 'school', 'points'
        )

        depth = 1


class TournamentDetailsSerializer(serializers.ModelSerializer):
    schools = serializers.SerializerMethodField()

    class Meta:
        model = Tournament
        fields = '__all__'

        depth = 1

    def get_schools(self, instance):
        schools = instance.schools.all().order_by('-points')
        return SchoolPointsSerializer(schools, many=True).data


class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True)
    school = SchoolSerializer()

    class Meta:
        model = Team
        fields = (
            'id', 'wins', 'losses', 'draws', 'players', 'school'
        )

        depth = 1


class TeamPlayersSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True)
    school = SchoolSerializer()

    class Meta:
        model = Team
        fields = (
            'id', 'players', 'school'
        )

        depth = 1


class MatchSerializer(serializers.ModelSerializer):
    team1 = TeamPlayersSerializer()
    team2 = TeamPlayersSerializer()

    score = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = (
            'id', 'team1', 'team2', 'score'
        )

        depth = 1

    def get_score(self, obj):
        score = obj.score.split("/")[:-1]
        return score
