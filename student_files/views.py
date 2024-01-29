from django.shortcuts import render
from rest_framework import viewsets, response
from .models import StudentFile
from .serializers import StudentFileSerializer

# Create your views here.

class  StudentFileViewSet(viewsets.ModelViewSet):
    queryset = StudentFile.objects.all()
    serializer_class = StudentFileSerializer

    def download_file(self, request, pk=None):
        student_file = self.get_object()
        path = student_file.file.path
        with open(path, 'rb') as file:
            response = response.FileResponse(file, content_type='application/text')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(student_file.file.name)
            return response
            