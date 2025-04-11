from django import forms
from .models import Material, Question, Category

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['content', 'categories', 'audio']

# 用于材料附带的问题输入（多个）
QuestionFormSet = forms.inlineformset_factory(
    Material,
    Question,
    fields=('question_text', 'question_audio'),
    extra=1,
    can_delete=False,
)

PRACTICE_MODE_CHOICES = [
    ('A', '键盘录入'),
    ('B', '手写记录'),
    ('C', '口述回答'),
]

class PracticeSettingForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="选择分类"
    )
    mode = forms.ChoiceField(
        choices=PRACTICE_MODE_CHOICES,
        widget=forms.RadioSelect,
        label="选择练习模式"
    )

class PracticeSettingForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="选择分类"
    )
    mode = forms.ChoiceField(  # ✅ 模式选择字段
        choices=PRACTICE_MODE_CHOICES,
        widget=forms.RadioSelect,
        label="选择练习模式"
    )