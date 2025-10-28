# training/views.py
import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from .models import Lesson, PetLessonProgress, LessonRating
from pets.models import Pet
from django.db.models import Count, Avg
from django.http import HttpResponseRedirect
from django.urls import reverse
import markdown
import bleach
from django.utils.safestring import mark_safe

# Определяем разрешённые теги и атрибуты для Bleach
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

@login_required
def toggle_lesson_status(request, pet_id, lesson_id, new_status):
    pet = get_object_or_404(Pet, id=pet_id)

    # Проверяем, является ли пользователь владельцем питомца
    if request.user not in pet.owners.all():
        return redirect('pets:list')

    lesson = get_object_or_404(Lesson, id=lesson_id)
    progress, created = PetLessonProgress.objects.get_or_create(pet=pet, lesson=lesson)

    progress.status = new_status
    progress.save()

    return redirect(f'/pets/{pet_id}/?tab=training')


@login_required
def lesson_list(request):
    lessons = Lesson.objects.annotate(avg_rating=Avg('ratings__rating')).order_by('title')
    return render(request, 'training/lesson_list.html', {'lessons': lessons})


@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    user_pets = Pet.objects.filter(owners=request.user)

    selected_pet_id = request.GET.get("pet")
    selected_pet = None
    progress = None
    status = None

    if selected_pet_id:
        selected_pet = get_object_or_404(Pet, id=selected_pet_id, owners=request.user)
        progress = PetLessonProgress.objects.filter(pet=selected_pet, lesson=lesson).first()
        status = progress.status if progress else None

    user_rating = None
    if request.user.is_authenticated:
        try:
            user_rating = LessonRating.objects.get(user=request.user, lesson=lesson)
        except LessonRating.DoesNotExist:
            pass

    average_rating = lesson.ratings.aggregate(avg=Avg('rating'))['avg']
    ratings_count = lesson.ratings.count()

    # Преобразование Markdown в HTML и очистка с помощью Bleach
    if lesson.text_content:
        html_content = markdown.markdown(lesson.text_content, extensions=['fenced_code', 'codehilite'])
        cleaned_html = bleach.clean(html_content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
        processed_text = mark_safe(cleaned_html)
    else:
        processed_text = ''

    context = {
        'lesson': lesson,
        'user_pets': user_pets,
        'selected_pet': selected_pet,
        'status': status,
        'user_rating': user_rating,
        'average_rating': average_rating,
        'ratings_count': ratings_count,
        'processed_text': processed_text,
    }

    return render(request, 'training/lesson_detail.html', context)


@login_required
def rate_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        pet_id = request.POST.get('pet_id')  # Получаем ID питомца из формы

        if rating_value:
            try:
                rating = int(rating_value)
                if 1 <= rating <= 5:
                    lesson_rating, created = LessonRating.objects.get_or_create(
                        user=request.user,
                        lesson=lesson,
                        defaults={'rating': rating}
                    )
                    if not created:
                        lesson_rating.rating = rating
                        lesson_rating.save()

                    # Формируем URL для редиректа с сохранением выбранного питомца
                    redirect_url = reverse('training:lesson_detail', args=[lesson.id])
                    if pet_id:
                        redirect_url += f'?pet={pet_id}'
                    return HttpResponseRedirect(redirect_url)

            except ValueError:
                pass

    # Если что-то пошло не так, тоже сохраняем параметр питомца
    redirect_url = reverse('training:lesson_detail', args=[lesson.id])
    pet_id = request.POST.get('pet_id')
    if pet_id:
        redirect_url += f'?pet={pet_id}'
    return HttpResponseRedirect(redirect_url)