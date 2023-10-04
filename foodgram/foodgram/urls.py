from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('cooking.urls')),
    path('admin/', admin.site.urls),
]
