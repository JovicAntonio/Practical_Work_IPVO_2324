"""
URL configuration for Student_Repository project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from student_files import views
from student_files.views import StudentFileViewSet
from django.conf import settings
from django.conf.urls.static import static
from . import settings
from django.views.generic.base import RedirectView
from django.urls import path, reverse_lazy

urlpatterns = [
    path('', RedirectView.as_view(url='list_data/')),
    path("admin/", admin.site.urls),
    path("add/", views.put_data, name="put_data"),
    path("list_data/", views.list_data, name="list_data"),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#urlpatterns += static(settings.ALLOWED_HOSTS, document_root=settings.ALLOWED_HOSTS)




