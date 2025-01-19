# management/commands/fetch.py
from django.core.management.base import BaseCommand
import feedparser   # To parse RSS feeds
from articles.models import BaseArticle, Category
from bs4 import BeautifulSoup  # To clean HTML from descriptions (HTML tags like <p>, <h1> are cleaned to extract only the content)
import html   # To convert HTML entities(&amp, &lt, etc.,) in descriptions to readable format(&amp -> &) using html.unescape(text)
from datetime import datetime, date, timedelta

class Command(BaseCommand):
    # Description of the command functionality
    help = "Parses RSS feeds from various sources and stores articles in the database"

    def clean_description(self, description):
        soup = BeautifulSoup(description, 'html.parser')   # Parse description to remove HTML tags
        text = soup.get_text()                             # Extract plain text from HTML

        cleaned_text = html.unescape(text)                 # Convert any HTML entities to characters (e.g., &amp; to &)

        return cleaned_text

    def parse_rss_feed(self, feed_url, source, exclude_category, category_group):
        """Parses the RSS feed and stores articles in the database based on the source."""
        feed = feedparser.parse(feed_url)   # Parse the RSS feed using feedparser

        for entry in feed.entries:

            category = 'unknown'            # Default category if no category found in RSS
            title = entry.get('title', 'No Title')[:100]
            link = entry.get('link', '')
            description = entry.get('description', '')[:300]
        
            cleaned_description = self.clean_description(description)   # Clean the description

            # Handle specific cases for known sources to categorize the article
            if source == "Deutsche Welle":
                published_at = entry.get('date', 'unknown')
                if published_at != 'unknown':
                    published_at = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ").date()
                else:
                    continue

                if 'tags' in entry:  # Feedparser converts <dc:subject> into 'tags'
                    category = entry.tags[0].term if entry.tags else 'unknown'

            elif source == "TechCrunch":
                published_at = entry.get('published', 'unknown')
                if published_at != 'unknown':
                    published_at = datetime.strptime(published_at, "%a, %d %b %Y %H:%M:%S %z").date()
                else:
                    continue

                if 'tags' in entry and len(entry.tags) > 0:
                    category = entry.tags[0].term[:10]  # Take the first category and truncate to 10 characters

             # Skip articles with excluded categories
            if category in exclude_category:
                continue  # Skip this iteration, do not save the article

            # Group articles into broader categories (e.g., "World" includes "News", "Climate")              <li><a href="{% url 'category_articles' category_name='Science' %}">Science</a></li>
            for group_name, group_categories in category_group.items():
                if category in group_categories:
                    category = group_name
                    break  # Exit loop once the group is found
            
            # Get or create the Category instance in the database
            category_obj, created = Category.objects.get_or_create(name=category)

            # Check if the article already exists in the database, and only add new ones
            if published_at >= (date.today() - timedelta(days=2)) and not BaseArticle.objects.filter(title=title).exists():
                # Create a new article entry in the database
                BaseArticle.objects.get_or_create(
                    title=title,
                    link=link,
                    description=cleaned_description,
                    category=category_obj,
                    source = source,
                    published_at = published_at
                )
            else:
                break


    def handle(self, *args, **kwargs):
        """Main handler that runs the command related to RSS feed parsing process."""

        #exclude unwanted categories
        exclude_category = ['Culture', 'Sports', 'Apps', 'Hardware', 'Health', 'TC']

        #group specific categories into the respective broader category
        category_group = {
            'World': ['World', 'News', 'Climate', 'Environment', 'Germany'],
            'Business' : ['Business'],
            'Science & Technology' : ['Transporta', 'AI', 'Venture', 'Security', 'Enterprise', 'Science', 'Space'],
        }

        Category.objects.all().delete()
        BaseArticle.objects.exclude(published_at=(date.today() - timedelta(days=2))).delete()
        
        # List of RSS feed URLs and their respective sources
        feeds = [
            ("https://rss.dw.com/rdf/rss-en-all", "Deutsche Welle"),
            ("https://techcrunch.com/feed/", "TechCrunch"),
        ]

        # Loop through each feed and call the parsing function
        for url, source in feeds:
            self.parse_rss_feed(url, source, exclude_category, category_group)

        # Output a success message after parsing all feeds
        self.stdout.write(self.style.SUCCESS("Successfully parsed all RSS feeds"))
