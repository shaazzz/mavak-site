# Generated by Django 3.0.8 on 2020-08-12 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_org_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='shenasname',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='student',
            name='verified',
            field=models.IntegerField(default=0),
        ),
    ]
