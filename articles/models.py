from django.db import models

# Create your models here.

# Model for Category to define different categories of articles
class Category(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name

# BaseArticle model for defining the structure of an article   
"""
The ForeignKey in Django is used to establish a one-to-many relationship between two models.
In this case, the ForeignKey in the BaseArticle model links each article to a specific category from the Category model.
Retrieving all articles for a given category is easier. 
The on_delete=models.CASCADE part tells Django to automatically delete all related articles when a category is deleted.
"""
class BaseArticle(models.Model):      
        
    title = models.CharField(max_length=100, unique=True)
    link = models.URLField()
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)  
    source = models.CharField(max_length=100, null=True, blank=True)
    published_at = models.DateField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Truncates the description to a specified length.
        """
        if self.description and len(self.description) > 250:
            # find the next_period after the 250th character
            next_period = self.description.find('.', 250)   
            # if next_period is found, truncate the description at that point
            # otherwise, truncate at 250 characters         
            if next_period != -1:
                self.description = self.description[:next_period + 1]
            else:
                self.description = self.description[:250]


        # Call the parent class's save method to save the article                   
        super().save(*args, **kwargs)
            
    def __str__(self):
        return self.title




