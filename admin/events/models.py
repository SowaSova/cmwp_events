from django.db import models
from django.core.exceptions import ValidationError


class WelcomeMessage(models.Model):
    """Модель для хранения приветственного сообщения"""
    text = models.TextField(verbose_name="Текст сообщения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Приветственное сообщение"
        verbose_name_plural = "Приветственное сообщение"

    def __str__(self):
        return f"Приветственное сообщение от {self.created_at.strftime('%d.%m.%Y')}"

    def save(self, *args, **kwargs):
        """Проверка, что существует только одно приветственное сообщение"""
        if not self.pk and WelcomeMessage.objects.exists():
            raise ValidationError("Приветственное сообщение уже существует. Вы можете только редактировать существующее.")
        return super().save(*args, **kwargs)


class Schedule(models.Model):
    """Модель для хранения расписания"""
    text = models.TextField(verbose_name="Текст расписания")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписание"

    def __str__(self):
        return f"Расписание от {self.created_at.strftime('%d.%m.%Y')}"

    def save(self, *args, **kwargs):
        """Проверка, что существует только одно расписание"""
        if not self.pk and Schedule.objects.exists():
            raise ValidationError("Расписание уже существует. Вы можете только редактировать существующее.")
        return super().save(*args, **kwargs)


class TelegramUser(models.Model):
    """Модель для хранения информации о пользователях Telegram"""
    telegram_id = models.BigIntegerField(primary_key=True, verbose_name="ID Telegram")
    full_name = models.CharField(max_length=255, verbose_name="Полное имя")
    username = models.CharField(max_length=255, blank=True, null=True, verbose_name="Username")
    real_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="ФИО")
    contacts = models.CharField(max_length=255, blank=True, null=True, verbose_name="Контактная информация")
    is_authorized = models.BooleanField(default=False, verbose_name="Авторизован")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Пользователь Telegram"
        verbose_name_plural = "Пользователи Telegram"
        ordering = ['-created_at']

    def __str__(self):
        if self.username:
            return f"{self.full_name} (@{self.username})"
        return self.full_name


class Speaker(models.Model):
    """Модель спикера"""
    name = models.CharField(max_length=255, verbose_name="ФИО")
    photo = models.ImageField(upload_to='speakers/', blank=True, null=True, verbose_name="Фото")
    description = models.TextField(verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Спикер"
        verbose_name_plural = "Спикеры"
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def unanswered_questions_count(self):
        """Возвращает количество неотвеченных вопросов для спикера"""
        return self.questions.filter(is_answered=False).count()
    
    unanswered_questions_count.short_description = "Неотвеченные вопросы"


class Expert(models.Model):
    """Модель эксперта"""
    name = models.CharField(max_length=255, verbose_name="ФИО")
    photo = models.ImageField(upload_to='experts/', blank=True, null=True, verbose_name="Фото")
    description = models.TextField(verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Эксперт"
        verbose_name_plural = "Эксперты"
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def unanswered_questions_count(self):
        """Возвращает количество неотвеченных вопросов для эксперта"""
        return self.questions.filter(is_answered=False).count()
    
    unanswered_questions_count.short_description = "Неотвеченные вопросы"


class Question(models.Model):
    """Модель вопроса"""
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='questions', verbose_name="Пользователь")
    speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE, related_name='questions', verbose_name="Спикер", null=True, blank=True)
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE, related_name='questions', verbose_name="Эксперт", null=True, blank=True)
    text = models.TextField(verbose_name="Текст вопроса")
    user_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Имя пользователя")
    is_answered = models.BooleanField(default=False, verbose_name="Отвечен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ['-created_at']

    def __str__(self):
        if self.speaker:
            return f"Вопрос для {self.speaker} от {self.user}"
        elif self.expert:
            return f"Вопрос для {self.expert} от {self.user}"
        return f"Вопрос от {self.user}"


class CompanyInfo(models.Model):
    """Информация о компании"""
    description = models.TextField('Описание')
    video = models.FileField('Видео', upload_to='company/', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Информация о компании'
        verbose_name_plural = 'Информация о компании'

    def __str__(self):
        return 'Информация о компании'
    
    def save(self, *args, **kwargs):
        """Проверка, что существует только одна запись информации о компании"""
        if not self.pk and CompanyInfo.objects.exists():
            raise ValidationError("Информация о компании уже существует. Вы можете только редактировать существующую.")
        return super().save(*args, **kwargs)


class CompanyLink(models.Model):
    """Ссылки компании"""
    company = models.ForeignKey(CompanyInfo, on_delete=models.CASCADE, related_name='links', verbose_name='Компания')
    title = models.CharField('Название', max_length=255)
    url = models.URLField('Ссылка')
    order = models.PositiveIntegerField('Порядок', default=0)
    
    class Meta:
        verbose_name = 'Ссылка компании'
        verbose_name_plural = 'Ссылки компании'
        ordering = ['order']

    def __str__(self):
        return self.title


class Survey(models.Model):
    """Модель опроса"""
    description = models.TextField(verbose_name="Описание")
    scheduled_time = models.DateTimeField(verbose_name="Время отправки")
    is_sent = models.BooleanField(default=False, verbose_name="Отправлен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Опрос"
        verbose_name_plural = "Опросы"
        ordering = ['-scheduled_time']

    def __str__(self):
        return f"Опрос от {self.scheduled_time.strftime('%d.%m.%Y %H:%M')}"


class SurveyQuestion(models.Model):
    """Модель вопроса опроса"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions', verbose_name="Опрос")
    text = models.TextField(verbose_name="Текст вопроса")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Вопрос опроса"
        verbose_name_plural = "Вопросы опроса"
        ordering = ['order']

    def __str__(self):
        return self.text[:50]


class SurveyQuestionOption(models.Model):
    """Модель варианта ответа на вопрос опроса"""
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'

    def __str__(self):
        return f"{self.text} (Вопрос: {self.question.text})"


class SurveyResponse(models.Model):
    """Модель ответа пользователя на опрос"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses', verbose_name="Опрос")
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='survey_responses', verbose_name="Пользователь")
    completed = models.BooleanField(default=False, verbose_name="Завершен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата начала")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")

    class Meta:
        verbose_name = "Ответ на опрос"
        verbose_name_plural = "Ответы на опросы"
        ordering = ['-created_at']
        unique_together = ['survey', 'user']

    def __str__(self):
        return f"Ответ от {self.user} на {self.survey}"


class SurveyOptionResponse(models.Model):
    """Модель выбранного варианта ответа"""
    response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='option_responses', verbose_name="Ответ на опрос")
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE, verbose_name="Вопрос")
    selected_option = models.ForeignKey(SurveyQuestionOption, on_delete=models.CASCADE, verbose_name="Выбранный вариант")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата ответа")

    class Meta:
        verbose_name = "Выбранный вариант"
        verbose_name_plural = "Выбранные варианты"
        ordering = ['question__order']
        unique_together = ['response', 'question']

    def __str__(self):
        return f"Ответ на вопрос {self.question} - {self.selected_option}"


class AfterQuestionText(models.Model):
    """Модель для хранения текста, который показывается после ввода вопроса"""
    text = models.TextField(verbose_name="Текст после вопроса", 
                           help_text="Этот текст будет показан пользователю после ввода вопроса и ФИО. Здесь можно попросить указать контактную информацию.")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Текст после вопроса"
        verbose_name_plural = "Текст после вопроса"

    def __str__(self):
        return f"Текст после вопроса от {self.created_at.strftime('%d.%m.%Y')}"
    
    def save(self, *args, **kwargs):
        """Проверка, что существует только один текст после вопроса"""
        if not self.pk and AfterQuestionText.objects.exists():
            raise ValidationError("Текст после вопроса уже существует. Вы можете только редактировать существующий.")
        return super().save(*args, **kwargs)
