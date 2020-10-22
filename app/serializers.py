from rest_framework import serializers
from .models import Journal


class JournalSerializer(serializers.ModelSerializer):

    category = serializers.StringRelatedField()  # so in api i get category name, not id
    login = serializers.StringRelatedField()
    class Meta:
        model = Journal
        fields = ("date", "login", "value", "category", "description" )