# Generated by Django 4.1.7 on 2023-03-08 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ButtonModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_button_id', models.CharField(max_length=50)),
                ('button', models.CharField(max_length=50)),
                ('to_button_id', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TextModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('button_id', models.CharField(max_length=50)),
                ('text', models.TextField()),
            ],
            options={
                'verbose_name': 'Текст',
                'verbose_name_plural': 'Тексты',
            },
        ),
        migrations.CreateModel(
            name='UserModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foreign_id', models.CharField(max_length=15)),
                ('stage', models.SmallIntegerField(default=0)),
                ('last_button_id', models.CharField(default='приветствие', max_length=50)),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
        ),
    ]
