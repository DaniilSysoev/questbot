from django.db import models


class UserModel(models.Model):
    foreign_id = models.CharField(max_length=15)
    stage = models.SmallIntegerField(default=0)
    last_button_id = models.CharField(max_length=50, default='приветствие')

    def __str__(self) -> str:
        return f'{self.foreign_id}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class TextModel(models.Model):
    button_id = models.CharField(max_length=50)
    text = models.TextField()

    def __str__(self) -> str:
        return f'{self.button_id}'
    
    class Meta:
        verbose_name = 'Текст'
        verbose_name_plural = 'Тексты'


class ButtonModel(models.Model):
    from_button_id = models.CharField(max_length=50)
    button = models.CharField(max_length=50)
    to_button_id = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Кнопка'
        verbose_name_plural = 'Кнопки'