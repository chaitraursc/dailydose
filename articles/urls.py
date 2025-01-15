from django.urls import path
from . import views

# URL patterns that map URL paths to views for the article application
urlpatterns = [
    path('', views.home, name='home'),  # Home page displaying all articles

    # URL pattern for category pages, dynamically routing based on category name
    # It takes a string 'category_name' and passes it to the 'category_articles' view
    path('category/<str:category_name>/', views.category_articles, name='category_articles'), 
]
