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


class Expert(models.Model):
    """Модель для хранения информации об экспертах"""
    name = models.CharField(max_length=255, verbose_name="ФИО")
    photo = models.ImageField(upload_to='experts/', blank=True, null=True, verbose_name="Фото")
    description = models.TextField(verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
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
    """Модель для хранения вопросов от пользователей"""
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='questions', verbose_name="Пользователь")
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE, related_name='questions', verbose_name="Эксперт")
    text = models.TextField(verbose_name="Текст вопроса")
    user_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="ФИО пользователя")
    is_answered = models.BooleanField(default=False, verbose_name="Отвечен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Вопрос от {self.user.full_name} для {self.expert.name}"
