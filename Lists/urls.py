
from django.urls import path

from . import views

from django.urls import path, include
from rest_framework.routers import DefaultRouter




urlpatterns = [

    # other non-DRF URLs here 
    path('create_list_with_element', views.create_list_with_element, name='create_list_with_element'),
    path('<int:list_id>/', views.get_list_with_elements, name='get_list_with_elements'),
    path('delete/<int:list_id>/', views.delete_list, name='delete_list'),
    path('update/<int:list_id>/', views.update_list, name='update_list'),

    #A user can Like a list 
    path('like_list/', views.like_list, name='like_list'),
]

