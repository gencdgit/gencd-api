from rest_framework import serializers
from extras_app import models

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Log
        fields = '__all__'