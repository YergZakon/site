from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('assistant/', views.assistant, name='assistant'),
    path('experts/', views.expert_list, name='experts'),
    path('experts/<int:pk>/', views.expert_detail, name='expert_detail'),
    path('documents/', views.document_list, name='documents'),
    path('publications/', views.publication_list, name='publications'),
    path('news/', views.news_list, name='news'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
    path('contacts/', views.contacts, name='contacts'),
    path('page/<slug:slug>/', views.page_detail, name='page'),
    path('set-language/<str:lang>/', views.set_language, name='set_language'),
]
