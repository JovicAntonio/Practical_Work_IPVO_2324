from django import forms
from .models import StudentFile

class StudentFileForm(forms.ModelForm):
    class Meta:
        model = StudentFile
        exclude = ['OriginalFileName', 'UidFileName', "fileSize", 'Classification', 'Confidence', 'wordCount']
        widgets = {
            'thesisDefenseDate' : forms.widgets.DateInput(attrs={'type': 'date'}, format='yyyy-MM-dd')
        }
