# Generated by Django 2.2.16 on 2022-07-05 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20220630_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Загрузка картинка', upload_to='posts/', verbose_name='Картинка'),
        ),
    ]
