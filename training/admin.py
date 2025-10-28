from django.contrib import admin
from .models import Lesson, PetLessonProgress

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

@admin.register(PetLessonProgress)
class PetLessonProgressAdmin(admin.ModelAdmin):
    list_display = ('pet', 'lesson', 'status', 'updated_at')
    list_filter = ('status', 'updated_at')
    search_fields = ('pet__name', 'lesson__title')

