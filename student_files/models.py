from django.db import models
from django.core.exceptions import ValidationError
import os
# Create your models here.
class StudentFile (models.Model):
    CHOICES = [
        ('dipl.', 'Diplomski rad'),
        ('mag.', 'Magistarski rad'),
        ('dr.', 'Doktorski rad'),
    ]


    title = models.CharField(max_length=100,null=True)
    file = models.FileField(upload_to="upload/")
    studentFirstName = models.CharField(max_length=50,null=True)
    studentLastName = models.CharField(max_length=50,null=True)
    thesisDefenseDate = models.DateField(null=True)
    thesisType = models.CharField(max_length=30, null=True, choices=CHOICES)
    thesisDefensePlace = models.CharField(max_length=100,null=True)
    wordCount = models.IntegerField(null=True)
    fileSize = models.IntegerField(null=True, blank=True)
    OriginalFileName = models.CharField(max_length=255, null=True, blank=True)
    UidFileName = models.CharField(max_length=255, null=True, blank=True)
    Classification = models.CharField(max_length=255, null=True, blank=True)
    Confidence = models.FloatField(null=True, blank=True)
    
    def clean(self):
        super().clean()
        if not self.file.name.endswith('.pdf'):
            raise ValidationError("Datoteka mora biti u PDF formatu.")