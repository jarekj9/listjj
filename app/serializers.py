from rest_framework import serializers
from .models import Journal


class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = ("date", "login", "value", "category", "description" )