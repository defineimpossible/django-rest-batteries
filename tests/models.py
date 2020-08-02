from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    is_deleted = models.BooleanField(default=False)


class Comment(models.Model):
    article = models.ForeignKey(
        'Article', on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField()
