from django.urls import path
from .import views

urlpatterns = [
    path('', views.show_graphs, name='show_graph'),
    path('box/', views.box, name='box')
    # เส้นทางอื่น ๆ
]
