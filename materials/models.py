from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название курса")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    currency = models.CharField(max_length=3, default='USD', verbose_name="Валюта")
    duration = models.IntegerField(verbose_name="Длительность (часов)")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Владелец"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        db_table = 'courses'

    def __str__(self):
        return self.title

class Lesson(models.Model):
    objects = None
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name=_('course')
    )
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    preview = models.ImageField(_('preview'), upload_to='lessons/previews/', blank=True, null=True)
    video_url = models.URLField(_('video URL'), blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = _('lesson')
        verbose_name_plural = _('lessons')

    def __str__(self):
        return self.title

class Payment(models.Model):
    CASH = 'cash'
    TRANSFER = 'transfer'
    STRIPE = 'stripe'

    PAYMENT_METHOD_CHOICES = [
        (CASH, 'Наличные'),
        (TRANSFER, 'Перевод на счет'),
        (STRIPE, 'Stripe'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Курс')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Урок')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма оплаты')
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default=TRANSFER,
        verbose_name='Способ оплаты'
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оплаты')
    is_successful = models.BooleanField(default=False, verbose_name='Оплата успешна')
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True, null=True,
                                                verbose_name='ID платежа в Stripe')

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']

    def __str__(self):
        return f'{self.user.email} - {self.amount} ({self.get_payment_method_display()})'

    def save(self, *args, **kwargs):
        # При успешной оплате предоставляем доступ к курсу/уроку
        if self.is_successful:
            self.grant_access()
        super().save(*args, **kwargs)

    def grant_access(self):
        """Предоставить доступ к курсу/уроку после успешной оплаты"""
        if self.course:
            # Логика предоставления доступа к курсу
            # Например, создание записи о доступе или отправка уведомления
            print(f"Предоставлен доступ к курсу {self.course.title} для пользователя {self.user.email}")

        if self.lesson:
            # Логика предоставления доступа к уроку
            print(f"Предоставлен доступ к уроку {self.lesson.title} для пользователя {self.user.email}")

class Subscription(models.Model):
    objects = None
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subscriptions', verbose_name="Курс")
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")
    is_active = models.BooleanField(default=True, verbose_name="Активная подписка")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ['user', 'course']  # Одна подписка на пользователя и курс

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"


class Product(models.Model):
    stripe_product_id = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Price(models.Model):
    stripe_price_id = models.CharField(max_length=100, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='usd')

    def __str__(self):
        return f"{self.product.name} - ${self.amount}"

