# Generated by Django 5.1.2 on 2025-04-05 02:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_input', models.CharField(blank=True, max_length=255, verbose_name='用户输入')),
                ('is_correct', models.BooleanField(null=True, verbose_name='是否正确')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictation.material')),
            ],
        ),
    ]
