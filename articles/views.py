# articles/views.py
import markdown
import bleach
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Article, SavedArticle
from django.db.models import Count, Avg

# Разрешённые теги и атрибуты для Bleach
ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
    'em', 'i', 'li', 'ol', 'strong', 'ul', 'h1', 'h2',
    'h3', 'h4', 'h5', 'h6', 'p', 'br', 'pre', 'img',
    'span'
]
ALLOWED_ATTRIBUTES = {
    '*': ['class', 'style'],
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title'],
}

def article_list(request):
    articles = Article.objects.annotate(saved_count=Count('savedarticle')).order_by('-created_at')
    
    processed_articles = []
    for article in articles:
        if article.content:
            # Преобразование Markdown в HTML
            html_content = markdown.markdown(article.content, extensions=['fenced_code', 'codehilite'])
            # Очистка HTML с помощью Bleach
            cleaned_html = bleach.clean(html_content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
            # Удаление HTML-тегов
            stripped_text = strip_tags(cleaned_html)
            # Сокращение до 30 слов
            words = stripped_text.split()
            if len(words) > 30:
                truncated_text = ' '.join(words[:30]) + '...'
            else:
                truncated_text = stripped_text
        else:
            truncated_text = ''
        
        processed_articles.append({
            'id': article.id,
            'title': article.title,
            'image': article.image.url if article.image else '',
            'truncated_content': truncated_text,
            'created_at': article.created_at,
            'saved_count': article.saved_count,
        })
    
    return render(request, 'articles/list.html', {'articles': processed_articles})


@login_required
def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    is_saved = SavedArticle.objects.filter(user=request.user, article=article).exists()

    # Обработка содержимого статьи
    if article.content:
        html_content = markdown.markdown(article.content, extensions=['fenced_code', 'codehilite'])
        cleaned_html = bleach.clean(html_content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
        processed_content = mark_safe(cleaned_html)
    else:
        processed_content = ''

    context = {
        'article': article,
        'is_saved': is_saved,
        'processed_content': processed_content,
    }
    return render(request, 'articles/detail.html', context)


@login_required
def save_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    SavedArticle.objects.get_or_create(user=request.user, article=article)
    return redirect('articles:detail', article_id=article.id)


@login_required
def unsave_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    SavedArticle.objects.filter(user=request.user, article=article).delete()
    return redirect('articles:detail', article_id=article.id)