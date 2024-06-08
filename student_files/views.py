from django.shortcuts import render, redirect
from rest_framework import viewsets, response
from .models import StudentFile
from .forms import StudentFileForm
from .serializers import StudentFileSerializer
from google.cloud import storage
from django.core.files.storage import default_storage
import os
import uuid
from django.conf import settings


# Create your views here.

class  StudentFileViewSet(viewsets.ModelViewSet):
    queryset = StudentFile.objects.all()
    serializer_class = StudentFileSerializer


def put_data(request):
    if request.method == 'POST' or request.method == 'PUT':
        form = StudentFileForm(request.POST, request.FILES)
        if form.is_valid():
            student_file = form.save(commit=False)
            uid = str(uuid.uuid4())
            original_file_name = request.FILES['file'].name
            extension = os.path.splitext(original_file_name)[1]
            uid_with_ext = uid + extension
            student_file.OriginalFileName = original_file_name
            student_file.UidFileName = uid_with_ext
            client = storage.Client(credentials=settings.GOOGLE_AUTH_CREDS)
            bucket = client.bucket("apvo-file-storage-v1.appspot.com")
            blob = bucket.blob(uid_with_ext)
            blob.upload_from_file(request.FILES['file'])

            form.save()
            return redirect('list_data')
    else:
        form = StudentFileForm()

    return render(request, 'student_files/put_data.html', {'form': form})

def list_data(request):
    filter_options = [        
        {'value': 'title', 'display': 'Title'},
        {'value': 'studentFirstName', 'display': 'First Name'},
        {'value': 'studentLastName', 'display': 'Last Name'},
        {'value': 'thesisDefenseDate', 'display': 'Thesis Defense Date'},
        {'value': 'thesisType', 'display': 'Thesis Type'},
        {'value': 'thesisDefensePlace', 'display': 'Thesis Defense Place'},
        ]
    
    if request.method == 'POST':
        filter_type = request.POST.get('filter_type')
        filter_value = request.POST.get('filter_value')

        if filter_type and filter_value:
            filter_kwargs = {f'{filter_type}__icontains': filter_value}
            queryset = StudentFile.objects.filter(**filter_kwargs)
        else:
            queryset = StudentFile.objects.all()
    else:
        queryset = StudentFile.objects.all()

    return render(request, 'student_files/list_data.html', {'queryset': queryset, 'filter_options': filter_options})