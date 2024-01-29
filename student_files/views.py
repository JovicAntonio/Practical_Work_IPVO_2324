from django.shortcuts import render
from rest_framework import viewsets, response
from .models import StudentFile
from .forms import StudentFileForm
from .serializers import StudentFileSerializer

# Create your views here.

class  StudentFileViewSet(viewsets.ModelViewSet):
    queryset = StudentFile.objects.all()
    serializer_class = StudentFileSerializer


def put_data(request):
    if request.method == 'POST' or request.method == 'PUT':
        form = StudentFileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_data')
    else:
        form = StudentFileForm()

    return render(request, 'student_files/put_data.html', {'form': form})


def list_data(request):
    data_list = StudentFile.objects.all()
    filtered_data = data_list

    if 'title' in request.GET:
        filter_name = request.GET['title']
        if filter_name:
            filtered_data = data_list.filter(title__icontains=filter_name)

    return render(request, 'student_files/list_data.html', {'data_list': data_list, 'filtered_data': filtered_data})