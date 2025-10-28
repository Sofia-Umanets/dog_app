# training/urls.py
from django.urls import path
from .views import toggle_lesson_status, lesson_list, lesson_detail, rate_lesson # Импортируйте rate_lesson

app_name = 'training'

urlpatterns = [
    path('lessons/', lesson_list, name='lesson_list'),
    path('lesson/<uuid:lesson_id>/', lesson_detail, name='lesson_detail'),
    # URL для отправки оценки
    path('lesson/<uuid:lesson_id>/rate/', rate_lesson, name='rate_lesson'),
    path('<uuid:pet_id>/<uuid:lesson_id>/set/<str:new_status>/', toggle_lesson_status, name='set_status'),
]
