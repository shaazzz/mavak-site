# Generated by Django 3.0.8 on 2020-08-04 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comment', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-date']},
        ),
        migrations.AddField(
            model_name='comment',
            name='private',
            field=models.BooleanField(default=False),
        ),
    ]