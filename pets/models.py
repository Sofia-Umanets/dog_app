import uuid
from django.db import models
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

class Pet(models.Model):
    GENDER_CHOICES = [
        ('M', 'Мальчик'),
        ('F', 'Девочка'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    birthday = models.DateField(null=True, blank=False)
    owners = models.ManyToManyField(User, related_name='pets')
    photo = models.ImageField(upload_to='pet_photos/', blank=True, null=True)
    breed = models.CharField(max_length=100, verbose_name='Порода', blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Вес (кг)', blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='Пол', blank=True, null=True)
    features = models.TextField(verbose_name='Особенности', blank=True, null=True, 
                               help_text='Аллергии, хронические заболевания и другие особенности питомца')



    def __str__(self):
        return self.name
    
    @property
    def age(self):
        if not self.birthday:
            return None
        today = date.today()
        years = today.year - self.birthday.year
        months = today.month - self.birthday.month
        days = today.day - self.birthday.day

        if days < 0:
            months -= 1
        if months < 0:
            years -= 1
            months += 12

        if years == 0:
            return f"{months} мес."
        elif months == 0:
            return f"{years} г."
        else:
            return f"{years} г. {months} мес."
