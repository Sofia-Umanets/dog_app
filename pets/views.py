
import uuid
from venv import logger
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Pet
from training.models import Lesson, PetLessonProgress
from calendarapp.models import Event, ReminderSettings
from datetime import date, timedelta, datetime, time
import copy

@login_required
def pets_list(request):
    pets = request.user.pets.all()
    return render(request, 'pets/pets_list.html', {'pets': pets})


@login_required
def pet_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        birthday = request.POST.get('birthday')
        weight = request.POST.get('weight') or None
        breed = request.POST.get('breed') or ''
        gender = request.POST.get('gender') or None
        photo = request.FILES.get('photo')
        features = request.POST.get('features') or ''  # Получаем данные из нового поля

        pet = Pet.objects.create(
            name=name,
            birthday=birthday,
            weight=weight,
            breed=breed,
            gender=gender,
            photo=photo,
            features=features  # Сохраняем в объект Pet
        )
        pet.owners.add(request.user)
        create_or_update_birthday_event(pet)
        return redirect('pets:list')

    return render(request, 'pets/pet_add.html')



@login_required
def pet_edit(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)

    if request.user not in pet.owners.all():
        return redirect('pets:list')

    if request.method == 'POST':
        pet.name = request.POST.get('name')
        birthday_input = request.POST.get('birthday')
        pet.birthday = birthday_input if birthday_input else None
        pet.weight = request.POST.get('weight') or None
        pet.breed = request.POST.get('breed') or ''
        pet.gender = request.POST.get('gender') or None
        pet.features = request.POST.get('features') or ''  # Обновляем поле features
        if request.FILES.get('photo'):
            pet.photo = request.FILES['photo']
        pet.save()
        Event.objects.filter(pet=pet, event_type='birthday', is_yearly=True).delete()
        create_or_update_birthday_event(pet)
        return redirect('pets:detail', pet_id=pet.id)

    return render(request, 'pets/pet_edit.html', {'pet': pet})


@login_required
def pet_detail(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)

    if request.user not in pet.owners.all():
        return redirect('pets:list')

    tab = request.GET.get('tab', 'info')
    context = {'pet': pet, 'tab': tab}

    if tab == 'info':
        birthday_today = False
        birthday_soon = None

        if pet.birthday:
            today = date.today()
            next_birthday = pet.birthday.replace(year=today.year)
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 3)

            delta = (next_birthday - today).days
            if delta == 0:
                birthday_today = True
            elif delta <= 7:
                birthday_soon = delta

        context.update({
            'birthday_today': birthday_today,
            'birthday_soon': birthday_soon,
        })

    elif tab == 'calendar':
        today = date.today()
        # Просто выводим ВСЕ события питомца (никаких автосозданий!)
        events = Event.objects.filter(pet=pet).order_by('date', 'time')
        context['events'] = events

    elif tab == 'training':
        lessons = Lesson.objects.all()
        completed_ids = PetLessonProgress.objects.filter(
            pet=pet, status='completed'
        ).values_list('lesson_id', flat=True)
        in_progress_ids = PetLessonProgress.objects.filter(
            pet=pet, status='in_progress'
        ).values_list('lesson_id', flat=True)

        lesson_filter = request.GET.get('filter', 'in_progress')
        if lesson_filter == 'completed':
            lessons = lessons.filter(id__in=completed_ids)
        else:
            lessons = lessons.filter(id__in=in_progress_ids)

        context.update({
            'lessons': lessons,
            'completed_lessons': list(completed_ids),
            'in_progress_lessons': list(in_progress_ids),
            'filter': lesson_filter,
        })

    return render(request, 'pets/pet_detail.html', context)

def create_or_update_birthday_event(pet):
    if not pet.birthday:
        return

    # Преобразуем строку в объект даты, если нужно
    if isinstance(pet.birthday, str):
        pet_birthday = datetime.strptime(pet.birthday, '%Y-%m-%d').date()
    else:
        pet_birthday = pet.birthday

    # Удаляем старое событие, если оно существует
    Event.objects.filter(pet=pet, event_type='birthday', is_yearly=True).delete()

    current_year = date.today().year
    for year in [current_year, current_year + 1, current_year + 2]:
        new_date = pet_birthday.replace(year=year)
        Event.objects.create(
            pet=pet,
            title='День рождения',
            event_type='birthday',
            date=new_date,
            time=None,
            duration_minutes=None,
            note='',
            is_yearly=True,
            is_done=False
        )

    # Настраиваем напоминание
    event = Event.objects.get(pet=pet, event_type='birthday', date=pet_birthday.replace(year=current_year))
    ReminderSettings.objects.update_or_create(
        event=event,
        defaults={
            'pet': pet,
            'repeat': True,
            'repeat_every': 365,
            'remind_at': time(9, 0)
        }
    )

@login_required
def pet_delete(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)

    if request.user not in pet.owners.all():
        return redirect('pets:list')

    if request.method == 'POST':
        pet.delete()
        return redirect('pets:list')

    return render(request, 'pets/pets_list.html', {'pet': pet})