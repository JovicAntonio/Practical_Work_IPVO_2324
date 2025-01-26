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
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer

# Create your views here.

class StudentFileViewSet(viewsets.ModelViewSet):
    queryset = StudentFile.objects.all()
    serializer_class = StudentFileSerializer

def pdf2text(pdf_path):
    word_count = 0
    extracted_keywords = ""
    extracted_sections = {}
    section_titles = ["Sažetak","Summary"]
    section_keywords = ["Ključne riječi", "Keywords"]
    pdf_document = fitz.open(pdf_path)
    
    text_found = False
    keywords_found = False

    with fitz.open(pdf_path) as doc:
        text = chr(12).join([page.get_text() for page in doc])
        word_count = len(text.strip(',.!?:;').split())

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        text = page.get_text()

        if not text_found:
            for title in section_titles:
                if title in text:
                    start_index = text.find(title)
                    section_text = text[start_index:]
                    extracted_sections[title] = section_text
                    text_found = True
                    break

        if not keywords_found:
            for keyword in section_keywords:
                if keyword in text:
                    for line in text.splitlines():
                        if keyword in line:
                            extracted_keywords = line.strip().replace(keyword, "").replace(":", "")
                            keywords_found = True
                            break
        
        if keywords_found and text_found:
            break

    pdf_document.close()
    summary = []
    keywords = []
    summary.append("".join(extracted_sections.values()).replace("\n", " "))
    keywords.append(extracted_keywords)

    return (summary, keywords, word_count)

def getClassification(text, keywords):
    new_text_embedding = settings.EMBEDDER.encode(text, convert_to_tensor=True)
    new_keyword_embedding = settings.EMBEDDER.encode(keywords, convert_to_tensor=True)

    settings.MODEL.eval()
    with torch.no_grad():
        new_prediction = settings.MODEL(new_text_embedding, new_keyword_embedding)
        probabilities = F.softmax(new_prediction)
        confidence = torch.max(probabilities).item()

        predicted_class = torch.argmax(new_prediction).item()
        predicted_label = settings.LABEL_ENCODER.inverse_transform([predicted_class])

    predicted_label = settings.LABEL_ENCODER.inverse_transform([predicted_class])
    return (predicted_label[0], confidence)

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

            pdf_text, pdf_keywords, word_count = pdf2text(tmp_file_path)
            try:
                os.remove(tmp_file_path)
            except:
                pass

            classificaton, confidence = getClassification(pdf_text, pdf_keywords)

            student_file.Classification = classificaton
            student_file.Confidence = confidence
            student_file.wordCount = word_count
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
