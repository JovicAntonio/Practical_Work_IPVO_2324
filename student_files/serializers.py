from rest_framework import serializers
from .models import StudentFile

class StudentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFile
        fields = '__all__'