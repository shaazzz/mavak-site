# Generated by Django 3.0.8 on 2020-08-15 12:05

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20200812_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='shenasname',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=users.models.get_file_path),
        ),
    ]
