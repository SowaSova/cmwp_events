from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from django.contrib.admin.widgets import AdminTextareaWidget
from django import forms
from django.db.models import Q
from .models import (
    WelcomeMessage, TelegramUser, Speaker, Expert, Question, CompanyInfo, CompanyLink, 
    Survey, SurveyQuestion, SurveyQuestionOption, SurveyResponse, SurveyOptionResponse, AfterQuestionText,
    EventInfo, Session, Topic
)


# Используем стандартную админку вместо кастомной
# class CustomAdminSite(AdminSite):
#     def each_context(self, request):
#         context = super().each_context(request)
#         context['extra_js'] = [
#             'admin/js/survey_options.js',
#         ]
#         return context
# admin_site = CustomAdminSite(name='admin')


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


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    """Админка для пользователей Telegram"""
    list_display = ('telegram_id', 'full_name', 'display_username', 'real_name', 'contacts', 'created_at')
    search_fields = ('telegram_id', 'full_name', 'username', 'real_name', 'contacts')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('telegram_id', 'full_name', 'username', 'real_name', 'contacts')
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
    """Инлайн для вопросов к спикеру"""
    model = Question
    extra = 0
    readonly_fields = ('user', 'text', 'user_name', 'created_at')
    fields = ('user', 'text', 'user_name', 'is_answered', 'created_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(self, 'speaker_inline') and self.speaker_inline:
            return qs.filter(speaker__isnull=False)
        elif hasattr(self, 'expert_inline') and self.expert_inline:
            return qs.filter(expert__isnull=False)
        return qs


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    """Админка спикеров"""
    list_display = ('name', 'display_photo', 'is_moderator', 'unanswered_questions_count', 'view_questions', 'created_at')
    search_fields = ('name',)
    list_filter = ('is_moderator',)
    readonly_fields = ('created_at', 'updated_at', 'display_photo_large')
    inlines = [QuestionInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'photo', 'display_photo_large', 'description', 'is_moderator')
        }),
        ('Информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_inlines(self, request, obj):
        inlines = super().get_inlines(request, obj)
        for inline in inlines:
            if inline == QuestionInline:
                inline.speaker_inline = True
        return inlines

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
        """Ссылка на вопросы спикера"""
        count = obj.questions.count()
        url = (
            reverse("admin:events_question_changelist")
            + "?"
            + urlencode({"speaker": f"{obj.id}"})
        )
        return format_html('<a href="{}">Все вопросы ({})</a>', url, count)
    view_questions.short_description = "Вопросы"
    
    def unanswered_questions_count(self, obj):
        """Возвращает количество неотвеченных вопросов"""
        return obj.questions.filter(is_answered=False).count()
    unanswered_questions_count.short_description = "Неотвеченные вопросы"
    
    def save_model(self, request, obj, form, change):
        """Проверяем, что модератор только один"""
        if obj.is_moderator:
            # Если устанавливаем модератора, снимаем флаг у всех остальных
            Speaker.objects.exclude(pk=obj.pk).filter(is_moderator=True).update(is_moderator=False)
        super().save_model(request, obj, form, change)


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

    def get_inlines(self, request, obj):
        inlines = super().get_inlines(request, obj)
        for inline in inlines:
            if inline == QuestionInline:
                inline.expert_inline = True
        return inlines

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
    
    def unanswered_questions_count(self, obj):
        """Возвращает количество неотвеченных вопросов"""
        return obj.questions.filter(is_answered=False).count()
    unanswered_questions_count.short_description = "Неотвеченные вопросы"


class SpeakerFilter(admin.SimpleListFilter):
    """Фильтр по спикерам с возможностью выбора нескольких"""
    title = 'Спикер'
    parameter_name = 'speaker'
    
    def lookups(self, request, model_admin):
        speakers = Speaker.objects.all()
        return [(str(speaker.id), speaker.name) for speaker in speakers]
    
    def queryset(self, request, queryset):
        if self.value():
            # Если выбран эксперт, игнорируем фильтр по спикеру
            if 'expert' in request.GET:
                return queryset
                
            return queryset.filter(speaker_id=self.value())
        return queryset


class ExpertFilter(admin.SimpleListFilter):
    """Фильтр по экспертам с возможностью выбора нескольких"""
    title = 'Эксперт'
    parameter_name = 'expert'
    
    def lookups(self, request, model_admin):
        experts = Expert.objects.all()
        return [(str(expert.id), expert.name) for expert in experts]
    
    def queryset(self, request, queryset):
        if self.value():
            # Если выбран спикер, игнорируем фильтр по эксперту
            if 'speaker' in request.GET:
                return queryset
                
            return queryset.filter(expert_id=self.value())
        return queryset


class RecipientTypeFilter(admin.SimpleListFilter):
    """Фильтр по типу получателя (спикер или эксперт)"""
    title = 'Тип получателя'
    parameter_name = 'recipient_type'
    
    def lookups(self, request, model_admin):
        return [
            ('speaker', 'Спикеры'),
            ('expert', 'Эксперты'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == 'speaker':
            return queryset.filter(speaker__isnull=False)
        elif self.value() == 'expert':
            return queryset.filter(expert__isnull=False)
        return queryset


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Админка для вопросов"""
    list_display = ('text_short', 'user', 'recipient_link', 'user_name', 'user_contacts_display', 'is_answered', 'created_at')
    list_filter = ('is_answered', RecipientTypeFilter, SpeakerFilter, ExpertFilter, 'created_at')
    search_fields = ('text', 'user_name', 'user__full_name', 'speaker__name', 'expert__name')
    readonly_fields = ('created_at', 'updated_at', 'user_contacts', 'user', 'speaker', 'expert', 'text', 'user_name')
    list_editable = ('is_answered',)
    fieldsets = (
        (None, {
            'fields': ('user', 'speaker', 'expert', 'text', 'user_name', 'user_contacts', 'is_answered')
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
    
    def user_contacts(self, obj):
        """Отображение контактной информации пользователя"""
        if obj.user and obj.user.contacts:
            return obj.user.contacts
        return "-"
    user_contacts.short_description = "Контактная информация"
    
    def user_contacts_display(self, obj):
        """Отображение контактной информации пользователя в списке"""
        if obj.user and obj.user.contacts:
            return obj.user.contacts
        return "-"
    user_contacts_display.short_description = "Контакты"
    
    def recipient_link(self, obj):
        """Ссылка на получателя вопроса (спикер или эксперт)"""
        if obj.speaker:
            url = (
                reverse("admin:events_question_changelist")
                + "?"
                + urlencode({"speaker": f"{obj.speaker.id}"})
            )
            return format_html('<a href="{}">{} (Спикер)</a>', url, obj.speaker.name)
        elif obj.expert:
            url = (
                reverse("admin:events_question_changelist")
                + "?"
                + urlencode({"expert": f"{obj.expert.id}"})
            )
            return format_html('<a href="{}">{} (Эксперт)</a>', url, obj.expert.name)
        return "-"
    recipient_link.short_description = "Получатель"
    
    def has_add_permission(self, request):
        """Запрещаем создание вопросов вручную"""
        return False


class CompanyLinkInline(admin.TabularInline):
    """Инлайн для ссылок компании"""
    model = CompanyLink
    extra = 1
    fields = ('title', 'url', 'order')


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    """Админка для информации о компании"""
    list_display = ('__str__', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'display_media')
    inlines = [CompanyLinkInline]
    fieldsets = (
        (None, {
            'fields': ('description', 'media', 'media_type', 'display_media'),
            'description': 'Загрузите медиа файл и выберите его тип (фото или видео)'
        }),
        ('Информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def display_media(self, obj):
        """Отображение медиа в форме редактирования"""
        if obj.media:
            if obj.media_type == 'photo':
                return format_html('<img src="{}" width="200" style="max-height: 300px; object-fit: contain;" />', obj.media.url)
            elif obj.media_type == 'video':
                return format_html(
                    '<video width="320" height="240" controls><source src="{}" type="video/mp4">Ваш браузер не поддерживает видео.</video>',
                    obj.media.url
                )
        return "-"
    display_media.short_description = "Предпросмотр"

    def has_add_permission(self, request):
        # Разрешаем создание только если нет ни одной записи
        return not CompanyInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление
        return False


@admin.register(EventInfo)
class EventInfoAdmin(admin.ModelAdmin):
    """Админка для информации о мероприятии"""
    list_display = ('__str__', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'display_media')
    fieldsets = (
        (None, {
            'fields': ('description', 'media', 'media_type', 'display_media'),
            'description': 'Загрузите медиа файл и выберите его тип (фото или видео)'
        }),
        ('Информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def display_media(self, obj):
        """Отображение медиа в форме редактирования"""
        if obj.media:
            if obj.media_type == 'photo':
                return format_html('<img src="{}" width="200" style="max-height: 300px; object-fit: contain;" />', obj.media.url)
            elif obj.media_type == 'video':
                return format_html(
                    '<video width="320" height="240" controls><source src="{}" type="video/mp4">Ваш браузер не поддерживает видео.</video>',
                    obj.media.url
                )
        return "-"
    display_media.short_description = "Предпросмотр"

    def has_add_permission(self, request):
        # Разрешаем создание только если нет ни одной записи
        return not EventInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление
        return False


class SurveyQuestionOptionInline(admin.TabularInline):
    """Инлайн для вариантов ответов"""
    model = SurveyQuestionOption
    extra = 0
    min_num = 0
    max_num = 0
    can_delete = False
    fields = []
    
    def has_add_permission(self, request, obj=None):
        return False


class SurveyQuestionForm(forms.ModelForm):
    """Форма для вопроса опроса с вариантами ответов"""
    # Убираем обязательное поле для варианта ответа, так как они будут добавляться через JavaScript
    # Добавляем скрытое поле для хранения JSON с вариантами ответов
    options_json = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = SurveyQuestion
        fields = ('text', 'order')
        widgets = {
            'text': AdminTextareaWidget(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        import json
        
        # Если это существующий вопрос, выводим информацию о вариантах ответах
        if self.instance and self.instance.pk:
            options = self.instance.options.all().order_by('order')
            
            # Создаем JSON с вариантами ответов для передачи в JavaScript
            options_data = []
            for option in options:
                options_data.append({
                    'order': option.order,
                    'text': option.text
                })
                
            # Добавляем JSON с вариантами ответов в initial и в поле формы
            options_json = json.dumps(options_data)
            self.initial['options_json'] = options_json
            self.fields['options_json'].initial = options_json
            
            # Добавляем атрибут data-options к виджету поля text
            self.fields['text'].widget.attrs['data-options'] = options_json

            # Добавляем атрибут data-options к виджету поля options_json
            self.fields['options_json'].widget.attrs['data-options'] = options_json
    
    def clean(self):
        """Проверяем, что есть хотя бы два варианта ответа"""
        cleaned_data = super().clean()

        option_count = 0
        
        # Проверяем поля в cleaned_data
        for key, value in cleaned_data.items():
            if key.startswith('option_') and value:
                option_count += 1
        
        # Если в cleaned_data недостаточно полей, проверяем в self.data
        if option_count < 2:
            option_count = 0
            for key in self.data:
                if key.startswith('questions-') and 'option_' in key and self.data[key].strip():
                    # Проверяем, что поле относится к текущей форме
                    parts = key.split('-')
                    if len(parts) >= 3 and parts[2].startswith('option_'):
                        form_index = parts[1]
                        form_id = f'questions-{form_index}'
                        if self.prefix == form_id or (not self.prefix and form_index == '0'):
                            option_count += 1
        
        if option_count < 2:
            raise forms.ValidationError("Необходимо указать минимум два варианта ответа")
        
        return cleaned_data
    
    def save(self, commit=True):
        import json
        from django.db import transaction
        
        # Получаем JSON с вариантами ответов
        options_json = self.cleaned_data.get('options_json', '')
        
        question = super().save(commit=False)
        
        if commit:
            with transaction.atomic():
                question.save()
                
                # Если есть JSON с вариантами ответов, обрабатываем его
                if options_json:
                    try:
                        options_data = json.loads(options_json)
                        
                        # Удаляем существующие варианты ответов
                        if question.pk:
                            existing_options = question.options.all()
                            existing_options.delete()
                        
                        # Создаем новые варианты ответов
                        for option_data in options_data:
                            order = option_data.get('order', 0)
                            text = option_data.get('text', '')
                            
                            if text.strip():  # Пропускаем пустые варианты
                                from events.models import SurveyQuestionOption
                                option = SurveyQuestionOption(
                                    question=question,
                                    order=order,
                                    text=text
                                )
                                option.save()
                    except Exception as e:
                        pass
        
        return question

    def as_div(self):
        """Переопределяем метод as_div, чтобы добавить атрибут data-options к форме"""
        import json
        
        # Получаем стандартный HTML-код формы
        html = super().as_div()
        
        # Если это существующий вопрос, добавляем атрибут data-options
        if self.instance and self.instance.pk:
            options = self.instance.options.all().order_by('order')
            options_data = []
            for option in options:
                options_data.append({
                    'order': option.order,
                    'text': option.text
                })
            options_json = json.dumps(options_data)
            
            # Добавляем скрытое поле с данными о вариантах ответов
            html += f'<input type="hidden" name="options_data" value="{options_json}" data-options="{options_json}" class="options-data">'
        
        return html


class SurveyQuestionInline(admin.StackedInline):
    """Инлайн для вопросов опроса с вариантами ответов"""
    model = SurveyQuestion
    form = SurveyQuestionForm
    extra = 0
    fields = ('text', 'order', 'options_json')
    verbose_name = "Вопрос"
    verbose_name_plural = "Вопросы"
    classes = ('survey-question-inline',)
    
    class Media:
        js = ('admin/js/jquery.init.js', 'admin/js/survey_options.js')
        css = {
            'all': ('admin/css/forms.css',)
        }
    
    def get_fieldsets(self, request, obj=None):
        """Скрываем поле options_json в форме, но оставляем его в fields"""
        return [(None, {'fields': ('text', 'order')})]
    
    def get_formset(self, request, obj=None, **kwargs):
        """Добавляем атрибут data-options к форме"""
        formset = super().get_formset(request, obj, **kwargs)
        
        # Сохраняем оригинальный метод __init__ формсета
        original_init = formset.__init__
        
        def new_init(self, *args, **kwargs):
            # Вызываем оригинальный метод __init__
            original_init(self, *args, **kwargs)
            
            # Добавляем атрибут data-options к каждой форме
            for form in self.forms:
                if form.instance and form.instance.pk:
                    import json
                    options = form.instance.options.all().order_by('order')
                    options_data = []
                    for option in options:
                        options_data.append({
                            'order': option.order,
                            'text': option.text
                        })
                    options_json = json.dumps(options_data)
                    form.fields['options_json'].initial = options_json
                    form.fields['options_json'].widget.attrs['data-options'] = options_json
                    
                    # Добавляем атрибут data-options к форме
                    if not hasattr(form, 'attr_data'):
                        form.attr_data = {}
                    form.attr_data['data-options'] = options_json
        
        # Заменяем метод __init__ формсета
        formset.__init__ = new_init
        
        return formset


class SurveyOptionResponseInline(admin.TabularInline):
    """Инлайн для выбранных вариантов ответов"""
    model = SurveyOptionResponse
    extra = 0
    readonly_fields = ('question', 'option_text', 'created_at')
    can_delete = False
    fields = ('question', 'option_text', 'created_at')

    def has_add_permission(self, request, obj=None):
        return False
        
    def option_text(self, obj):
        """Возвращает текст выбранного варианта ответа"""
        return obj.selected_option.text if obj.selected_option else "-"
    option_text.short_description = "Ответ"


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    """Админка для опросов"""
    list_display = ('__str__', 'scheduled_time', 'is_sent', 'created_at', 'get_questions_count', 'get_responses_count')
    list_filter = ('is_sent',)
    search_fields = ('description',)
    readonly_fields = ('is_sent', 'created_at', 'updated_at')
    inlines = [SurveyQuestionInline]
    fieldsets = (
        (None, {
            'fields': ('description', 'scheduled_time', 'is_sent'),
            'description': 'Укажите описание опроса и время его отправки. После создания опроса добавьте вопросы и варианты ответов ниже.'
        }),
        ('Информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    save_on_top = True
    
    class Media:
        js = ('admin/js/jquery.init.js', 'admin/js/survey_options.js')
        css = {
            'all': ('admin/css/forms.css',)
        }

    def get_questions_count(self, obj):
        """Возвращает количество вопросов в опросе"""
        return obj.questions.count()
    get_questions_count.short_description = "Вопросы"

    def get_responses_count(self, obj):
        """Возвращает количество ответов на опрос"""
        return obj.responses.count()
    get_responses_count.short_description = "Ответы"


# Скрываем модель SurveyQuestion из админки
# @admin_site.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    """Админка для вопросов опроса"""
    list_display = ('text', 'survey', 'order')
    list_filter = ('survey',)
    search_fields = ('text', 'survey__description')
    inlines = [SurveyQuestionOptionInline]
    form = SurveyQuestionForm
    fieldsets = (
        (None, {
            'fields': ('survey', 'text', 'order', 'options_json'),
        }),
    )
    
    class Media:
        js = ('admin/js/jquery.init.js', 'admin/js/survey_options.js')
        css = {
            'all': ('admin/css/forms.css',),
        }

    def get_options_count(self, obj):
        """Возвращает количество вариантов ответа на вопрос"""
        return obj.options.count()
    get_options_count.short_description = "Варианты"
    
    def has_add_permission(self, request):
        """Запрещаем создание вопросов отдельно от опроса"""
        return False


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    """Админка для ответов на опросы"""
    list_display = ('__str__', 'survey', 'user', 'created_at')
    list_filter = ('survey',)
    search_fields = ('user__full_name', 'user__username', 'survey__description')
    readonly_fields = ('survey', 'user', 'created_at')
    inlines = [SurveyOptionResponseInline]
    fieldsets = (
        (None, {
            'fields': ('survey', 'user')
        }),
        ('Информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return False


# Скрываем модель SurveyQuestionOption из админки
# @admin.register(SurveyQuestionOption)
class SurveyQuestionOptionAdmin(admin.ModelAdmin):
    """Админка для вариантов ответов на вопросы опроса"""
    list_display = ('text', 'question', 'order')
    list_filter = ('question__survey',)
    search_fields = ('text', 'question__text')
    ordering = ('question', 'order')


@admin.register(AfterQuestionText)
class AfterQuestionTextAdmin(admin.ModelAdmin):
    """Админка для текста после вопроса"""
    list_display = ('__str__', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('text',),
            'description': 'Этот текст будет показан пользователю после ввода вопроса и ФИО. Здесь можно попросить указать контактную информацию.'
        }),
        ('Информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Разрешаем создание только если нет ни одной записи
        return not AfterQuestionText.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление
        return False


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    """Админка сессий"""
    list_display = ('title', 'order', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('order',)


class TopicInline(admin.TabularInline):
    """Инлайн для тем в сессии"""
    model = Topic
    extra = 1
    fields = ('title', 'order')


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """Админка тем"""
    list_display = ('title', 'session', 'order', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('session',)
    list_editable = ('order',)
    filter_horizontal = ('speakers',)
    fieldsets = (
        (None, {
            'fields': ('session', 'title', 'description', 'order')
        }),
        ('Спикеры', {
            'fields': ('speakers',)
        }),
    )
