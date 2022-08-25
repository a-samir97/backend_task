from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class UserBalance(serializers.Serializer):
    amount = serializers.FloatField()


class StockSerializer(serializers.Serializer):
    name = serializers.CharField()
    total = serializers.IntegerField()
    lower_bound = serializers.FloatField()
    upper_bound = serializers.FloatField()