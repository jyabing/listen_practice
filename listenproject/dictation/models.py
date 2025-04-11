from django.db import models
from django.contrib.auth.models import User

# 听写分类
class Category(models.Model):
    name = models.CharField("分类名", max_length=100)

    def __str__(self):
        return self.name

# 听写材料（单词或句子）
class Material(models.Model):
    content = models.CharField("听写内容", max_length=255)
    categories = models.ManyToManyField(Category, verbose_name="所属分类")
    audio = models.FileField("音频文件（可选）", upload_to="audio/materials/", blank=True, null=True)

    def __str__(self):
        return self.content

# 听写问题（提问内容）
class Question(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="questions")
    question_text = models.CharField("问题内容", max_length=255)
    question_audio = models.FileField("问题音频（可选）", upload_to="audio/questions/", blank=True, null=True)

    def __str__(self):
        return f"问题：{self.question_text}（材料：{self.material}）"

class PracticeSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    mode = models.CharField(max_length=1, choices=[('A', '键盘'), ('B', '手写'), ('C', '口述')])
    interval = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AnswerRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey(PracticeSession, on_delete=models.CASCADE, null=True, blank=True)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    user_input = models.CharField(max_length=255, blank=True)
    is_correct = models.BooleanField(null=True)
    audio_data = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
