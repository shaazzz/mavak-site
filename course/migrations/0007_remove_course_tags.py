# Generated by Django 3.0.8 on 2020-09-06 05:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0006_tag'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='tags',
        ),
    ]