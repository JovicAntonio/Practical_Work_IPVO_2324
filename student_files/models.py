from django.db import models

# Create your models here.
class StudentFile (models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to="student_files/files/")

    def __str__(self):
        return self.title