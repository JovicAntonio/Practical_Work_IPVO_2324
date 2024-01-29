from django import forms
from .models import StudentFile


class StudentFileForm(forms.ModelForm):
    class Meta:
        model = StudentFile
        fields = '__all__'

def put_data(request):
    if request.method == 'POST':
        form = StudentFileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_data')
    else:
        form = StudentFileForm()

    return render(request, 'add_data.html', {'form': form})


def list_data(request):
    data_list = StudentFile.objects.all()
    filtered_data = data_list

    if 'title' in request.GET:
        name_filter = request.GET['title']
        if name_filter:
            filtered_data = data_list.filter(name__icontains=name_filter)

    return render(request, 'list_data.html', {'data_list': data_list, 'filtered_data': filtered_data})