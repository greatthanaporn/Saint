from django.urls import path
from .import views

urlpatterns = [
    path('', views.show_graph, name='show_graph'),
    # เส้นทางอื่น ๆ
]