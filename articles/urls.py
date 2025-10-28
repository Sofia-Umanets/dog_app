from django.urls import path
from .views import article_detail, article_list, save_article, unsave_article

app_name = 'articles'

urlpatterns = [
    path('', article_list, name='list'),
    path('<uuid:article_id>/', article_detail, name='detail'),
    path('<uuid:article_id>/save/', save_article, name='save'),
    path('<uuid:article_id>/unsave/', unsave_article, name='unsave'),
]
