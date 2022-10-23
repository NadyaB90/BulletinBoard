from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


class CategoryModel(models.Model):

    CHOISES = [
        ('TK', 'Tanks'),
        ('HE', 'Heals'),
        ('DD', 'DD'),
        ('MH', 'Merchants'),
        ('GM', 'Guild Masters'),
        ('QG', 'Quest Givers'),
        ('BS', 'Blacksmiths'),
        ('TN', 'Tanners'),
        ('PM', 'Potion Makers'),
        ('SM', 'Spell Masters'),
    ]

    category_name = models.CharField(max_length=255, choices=CHOISES, unique=True)
    subscribers = models.ManyToManyField(User, null=True, blank=True, related_name='subscriber')

    def __str__(self):
        return f'{self.category_name}'


class Bulletin(models.Model):
    title = models.CharField(max_length=100, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    file = models.FileField(upload_to='files/', blank=True)
    bulletin_category = models.ForeignKey(CategoryModel, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('bulletin-detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    bulletin = models.ForeignKey(Bulletin, related_name="comments", on_delete=models.CASCADE)
    username = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    body = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' % (self.bulletin.title, self.username)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('comment_create', kwargs={'pk': self.pk})
