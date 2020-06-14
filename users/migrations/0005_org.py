# Generated by Django 2.2.12 on 2020-06-14 13:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0004_student_shomare'),
    ]

    operations = [
        migrations.CreateModel(
            name='Org',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ostan', models.CharField(max_length=50)),
                ('shomare', models.CharField(max_length=50)),
                ('goone', models.CharField(choices=[('D', 'دبیرستان (متوسطه دوره دوم)'), ('R', 'راهنمایی (متوسطه دوره اول)'), ('S', 'مرکز سمپاد')], max_length=1)),
                ('verified', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
