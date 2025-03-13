from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from .models import WelcomeMessage, TelegramUser, Expert, Question, Schedule


@admin.register(WelcomeMessage)
class WelcomeMessageAdmin(admin.ModelAdmin):
    """Админка для приветственного сообщения"""
    list_display = ('__str__', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('text',)
        }),
        ('Информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Разрешаем создание только если нет ни одного сообщения
        return not WelcomeMessage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление
        return False


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    """Админка для расписания"""
    list_display = ('__str__', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('text',)
        }),
        ('Информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Разрешаем создание только если нет ни одного расписания
        return not Schedule.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление
        return False


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    """Админка для пользователей Telegram"""
    list_display = ('telegram_id', 'full_name', 'display_username', 'real_name', 'created_at')
    search_fields = ('telegram_id', 'full_name', 'username', 'real_name')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('telegram_id', 'full_name', 'username', 'real_name')
        }),
        ('Информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def display_username(self, obj):
        """Отображение username с @"""
        if obj.username:
            return f"@{obj.username}"
        return "-"
    display_username.short_description = "Username"


class QuestionInline(admin.TabularInline):
    """Инлайн для вопросов к эксперту"""
    model = Question
    extra = 0
    readonly_fields = ('user', 'text', 'user_name', 'created_at')
    fields = ('user', 'text', 'user_name', 'is_answered', 'created_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Expert)
class ExpertAdmin(admin.ModelAdmin):
    """Админка для экспертов"""
    list_display = ('name', 'display_photo', 'unanswered_questions_count', 'view_questions', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at', 'display_photo_large')
    list_filter = ('created_at',)
    inlines = [QuestionInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'photo', 'display_photo_large', 'description')
        }),
        ('Информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def display_photo(self, obj):
        """Отображение миниатюры фото в списке"""
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />', obj.photo.url)
        return "-"
    display_photo.short_description = "Фото"

    def display_photo_large(self, obj):
        """Отображение фото в форме редактирования"""
        if obj.photo:
            return format_html('<img src="{}" width="200" style="max-height: 300px; object-fit: contain;" />', obj.photo.url)
        return "-"
    display_photo_large.short_description = "Предпросмотр фото"
    
    def view_questions(self, obj):
        """Ссылка на вопросы эксперта"""
        count = obj.questions.count()
        url = (
            reverse("admin:events_question_changelist")
            + "?"
            + urlencode({"expert": f"{obj.id}"})
        )
        return format_html('<a href="{}">Все вопросы ({})</a>', url, count)
    view_questions.short_description = "Вопросы"


class ExpertFilter(admin.SimpleListFilter):
    """Фильтр по экспертам с отображением фото"""
    title = 'Эксперт'
    parameter_name = 'expert'
    
    def lookups(self, request, model_admin):
        experts = Expert.objects.all()
        return [(expert.id, expert.name) for expert in experts]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(expert__id=self.value())
        return queryset


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Админка для вопросов"""
    list_display = ('text_short', 'user', 'expert_link', 'user_name', 'is_answered', 'created_at')
    list_filter = ('is_answered', ExpertFilter, 'created_at')
    search_fields = ('text', 'user_name', 'user__full_name', 'expert__name')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_answered',)
    fieldsets = (
        (None, {
            'fields': ('user', 'expert', 'text', 'user_name', 'is_answered')
        }),
        ('Информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def text_short(self, obj):
        """Сокращенный текст вопроса"""
        if len(obj.text) > 50:
            return f"{obj.text[:50]}..."
        return obj.text
    text_short.short_description = "Вопрос"
    
    def expert_link(self, obj):
        """Ссылка на эксперта с возможностью фильтрации"""
        url = (
            reverse("admin:events_question_changelist")
            + "?"
            + urlencode({"expert": f"{obj.expert.id}"})
        )
        return format_html('<a href="{}">{}</a>', url, obj.expert.name)
    expert_link.short_description = "Эксперт"
    expert_link.admin_order_field = 'expert__name'
