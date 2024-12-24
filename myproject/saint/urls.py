from django.urls import path
from .import views

urlpatterns = [
    path('', views.show_graphs, name='show_graph'),

    # เส้นทางอื่น ๆ
]
