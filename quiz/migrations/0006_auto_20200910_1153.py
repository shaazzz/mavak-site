# Generated by Django 3.0.8 on 2020-09-10 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0005_collection_picture_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='picture_url',
            field=models.URLField(default='http://uupload.ir/files/e799_comb.png'),
        ),
    ]