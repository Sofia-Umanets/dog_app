# articles/models.py
from django.db import models
from django.db.models import Count
import uuid

# Если CustomUser в отдельном приложении accounts:
try:
    from accounts.models import CustomUser
except ImportError:
    # Если CustomUser не найден, предположим, что используется стандартная модель User
    from django.contrib.auth import get_user_model
    CustomUser = get_user_model()


class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='article_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def saved_by_count(self):
        """Возвращает количество пользователей, добавивших статью в избранное."""
        return self.savedarticle_set.count()

    def __str__(self):
        return self.title

class SavedArticle(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='saved_articles')
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')
        verbose_name = "Сохраненная статья"
        verbose_name_plural = "Сохраненные статьи"

    def __str__(self):
        return f'{self.user.username} saved {self.article.title}'

