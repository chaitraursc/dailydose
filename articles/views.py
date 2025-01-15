from django.shortcuts import render
from articles.models import BaseArticle
#from django.db.models import Count

# Fetch 2 latest articles from each category and render it in home page
def home(request):
    
    main_categories = ['World', 'Business', 'Science & Technology']   # Main categories to be displayed
    
    articles_by_category = {} # Dictionary to store articles categorized by category names

    # Loop through each category name and fetch the latest 2 articles (order_by('-id')[:2])
    for category_name in main_categories:
        category_articles = BaseArticle.objects.filter(category__name=category_name).order_by('-id')[:2]
        articles_by_category[category_name] = category_articles
    
    return render(request, 'articles/home.html', {'articles_by_category': articles_by_category})

# Fetch all articles for a given category and render the category page(latest first)
def category_articles(request, category_name):

    articles = BaseArticle.objects.filter(category__name=category_name).order_by('-id')
    return render(request, 'articles/category_articles.html', {'category_name': category_name, 'articles': articles})
