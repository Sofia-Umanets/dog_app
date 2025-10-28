import uuid
from django.db import models
from accounts.admin import CustomUser
from pets.models import Pet


class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video = models.FileField(upload_to='training_videos/', blank=True, null=True)
    text_content = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='lesson_covers/', blank=True, null=True)

    def __str__(self):
        return self.title


class PetLessonProgress(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'Проходит сейчас'),
        ('completed', 'Завершено'),
    ]

    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('pet', 'lesson')

    def __str__(self):
        return f'{self.pet.name} — {self.lesson.title} — {self.get_status_display()}'
    

class LessonRating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) # Связываем с пользователем
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='ratings') # Связываем с уроком, related_name для удобства
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)]) # Оценка от 1 до 5 (можно изменить)

    class Meta:
        unique_together = ('user', 'lesson') # Гарантируем, что пользователь может оценить урок только один раз
        verbose_name = "Оценка урока"
        verbose_name_plural = "Оценки уроков"

    def __str__(self):
        return f'Оценка {self.rating} от {self.user.username} для урока "{self.lesson.title}"'

