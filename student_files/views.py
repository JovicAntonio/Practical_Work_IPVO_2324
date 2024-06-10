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
from django.http import Http404
from django.views.decorators.clickjacking import xframe_options_sameorigin, xframe_options_exempt
from datetime import timedelta
import fitz
import torch

# Create your views here.

class StudentFileViewSet(viewsets.ModelViewSet):
    queryset = StudentFile.objects.all()
    serializer_class = StudentFileSerializer

def pdf2text(pdf_path):
    pdf_document = fitz.open(pdf_path)
    
    text = ""
    
    for page_num in range(5, 10):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    
    return text

def getClassification(text):
    # Tokenize the input text
    inputs = settings.TOKENIZER(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

    # Get model predictions
    with torch.no_grad():
        outputs = settings.MODEL(**inputs)
        logits = outputs.logits
        predicted_class_id = torch.argmax(logits, dim=-1).item()

    # Decode the predicted class ID to get the label
    predicted_label = settings.LABELS[predicted_class_id]
    return predicted_label

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
            student_file.fileSize = student_file.file.size

            client = storage.Client(credentials=settings.GOOGLE_AUTH_CREDS)
            bucket = client.bucket("apvo-file-storage-v1.appspot.com")
            blob = bucket.blob(uid_with_ext)
            blob.upload_from_file(request.FILES['file'])

            tmp_file_path = os.path.join(settings.MEDIA_ROOT, original_file_name)

            with open(tmp_file_path, 'wb+') as destination:
                for chunk in request.FILES['file'].chunks():
                    destination.write(chunk)

            pdf_text = pdf2text(tmp_file_path)
            try:
                os.remove(tmp_file_path)
            except:
                pass

            classificaton = getClassification(pdf_text)

            student_file.Classification = classificaton


            form.save()
            return redirect('list_data')
    else:
        form = StudentFileForm()

    return render(request, 'student_files/put_data.html', {'form': form})

def list_data(request):
    filter_options = [        
        {'value': 'title', 'display': 'Naslov'},
        {'value': 'studentFirstName', 'display': 'Ime'},
        {'value': 'studentLastName', 'display': 'Prezime'},
        {'value': 'thesisDefenseDate', 'display': 'Datum obrane'},
        {'value': 'thesisType', 'display': 'Tip studentskog rada'},
        {'value': 'thesisDefensePlace', 'display': 'Mjesto obrane'},
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

@xframe_options_exempt
def student_file_detail(request, id):
    storage_url = ""
    try:
        student_file = StudentFile.objects.get(id=id)

        client = storage.Client(credentials=settings.GOOGLE_AUTH_CREDS)
        bucket = client.bucket("apvo-file-storage-v1.appspot.com")
        blob = bucket.blob(student_file.UidFileName)
        storage_url = blob.generate_signed_url(expiration=timedelta(days=1), method='GET')

    except StudentFile.DoesNotExist:
        raise Http404("Takav dokument ne postoji!")
    return render(request, 'student_files/student_file_detail.html', {'student_file' : student_file, 'storage_url' : storage_url})


def delete_file_detail(request, id):
    storage_url = ""
    try:
        student_file = StudentFile.objects.get(id=id)
        client = storage.Client(credentials=settings.GOOGLE_AUTH_CREDS)
        bucket = client.bucket("apvo-file-storage-v1.appspot.com")
        blob = bucket.blob(student_file.UidFileName)
        blob.delete()
        student_file.delete()

    except StudentFile.DoesNotExist:
        raise Http404("Došlo je do greške prilikom brisanja. Takav dokument ne postoji!")

    return render(request, 'student_files/delete_popup.html')
