from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserChangeForm, CustomUserCreationForm
from django.utils.html import format_html

CustomUser = get_user_model()

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    
    # Добавляем новые поля в основной набор полей
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'email', 'avatar', 'phone', 'birth_date', 'bio'),
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Набор полей при создании пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 
                'email', 
                'password1', 
                'password2', 
                'avatar',
                'phone',
                'birth_date',
                'bio'
            ),
        }),
    )

    # Отображаемые поля в списке пользователей
    list_display = [
        'username', 
        'email', 
        'display_avatar', 
        'phone',
        'birth_date',
        'is_staff'
    ]
    
    # Поля для поиска
    search_fields = ['username', 'email', 'phone', 'first_name', 'last_name']
    
    # Поля для фильтрации
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined']
    
    # Поля, по которым можно производить сортировку
    ordering = ['-date_joined']

    def display_avatar(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%;" />',
                obj.avatar.url
            )
        return "Нет аватара"
    display_avatar.short_description = 'Аватар'

    # Добавляем быстрые фильтры
    def get_list_filter(self, request):
        return super().get_list_filter(request) + ('birth_date',)

    # Настройка отображения в списке
    list_per_page = 25  # количество записей на странице
    list_max_show_all = 1000  # максимальное количество записей при показе всех
    show_full_result_count = True

    # Добавляем действия
    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Активировать выбранных пользователей"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Деактивировать выбранных пользователей"

    # Настройка readonly полей
    def get_readonly_fields(self, request, obj=None):
        if obj:  # если редактируем существующего пользователя
            return ['date_joined', 'last_login']
        return []

admin.site.register(CustomUser, CustomUserAdmin)


