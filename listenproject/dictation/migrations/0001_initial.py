# Generated by Django 5.1.2 on 2025-04-03 06:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='分类名')),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=255, verbose_name='听写内容')),
                ('audio', models.FileField(blank=True, null=True, upload_to='audio/materials/', verbose_name='音频文件（可选）')),
                ('categories', models.ManyToManyField(to='dictation.category', verbose_name='所属分类')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=255, verbose_name='问题内容')),
                ('question_audio', models.FileField(blank=True, null=True, upload_to='audio/questions/', verbose_name='问题音频（可选）')),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='dictation.material')),
            ],
        ),
    ]
