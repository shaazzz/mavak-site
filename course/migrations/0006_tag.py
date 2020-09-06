# Generated by Django 3.0.8 on 2020-09-06 05:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
        ('course', '0005_auto_20200906_0943'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.Course')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Tag')),
            ],
        ),
    ]