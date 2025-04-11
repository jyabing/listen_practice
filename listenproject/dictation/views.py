import json
import random
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Material, Category, Question, AnswerRecord, PracticeSession
from .forms import MaterialForm, QuestionFormSet, PracticeSettingForm
from django.db.models import Count, Q, Prefetch
from datetime import datetime
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict


def home(request):
    return render(request, 'dictation/home.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 注册后自动登录
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def create_material(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        formset = QuestionFormSet(request.POST, request.FILES, prefix='question_set')
        if form.is_valid() and formset.is_valid():
            material = form.save()
            formset.instance = material
            formset.save()
            return redirect('home')
    else:
        form = MaterialForm()
        formset = QuestionFormSet(prefix='question_set')
    return render(request, 'dictation/create_material.html', {'form': form, 'formset': formset})

@login_required
def play_material(request, pk):
    material = get_object_or_404(Material, pk=pk)
    return render(request, 'dictation/play_material.html', {'material': material})

@login_required
def practice_setting(request):
    if request.method == 'POST':
        form = PracticeSettingForm(request.POST)
        if form.is_valid():
            categories = form.cleaned_data['categories']
            mode = form.cleaned_data['mode']  # ✅ 获取 mode

            request.session['practice_material_ids'] = list(Material.objects.filter(categories__in=categories).values_list('id', flat=True))
            request.session['practice_mode'] = mode  # ✅ 保存 mode 到 session

            return redirect('practice_play')
    else:
        form = PracticeSettingForm()

    return render(request, 'dictation/practice_setting.html', {'form': form})

@login_required
def practice_play(request):
    material_ids = request.session.get('practice_material_ids')
    mode = request.session.get('practice_mode')

    if not material_ids or not mode:
        return redirect('practice_setting')

    materials = list(Material.objects.filter(id__in=material_ids).prefetch_related('questions'))
    random.shuffle(materials)

    session_obj = PracticeSession.objects.create(
        user=request.user,
        mode=mode,
        interval=None  # interval 不再使用
    )

    request.session['current_session_id'] = session_obj.id
    request.session['current_play_order'] = [m.id for m in materials]

    # ✅ 根据模式选择模板
    if mode == 'A':
        template_name = 'dictation/practice_play_A.html'
    elif mode == 'B':
        template_name = 'dictation/practice_play_B.html'
    elif mode == 'C':
        template_name = 'dictation/practice_play_C.html'
    else:
        return redirect('practice_setting')  # 万一取不到

    return render(request, template_name, {
        'materials': json.dumps([{
            'id': m.id,
            'content': m.content,
            'audio': m.audio.url if m.audio else '',
            'questions': [
                {'question_text': q.question_text,
                 'question_audio': q.question_audio.url if q.question_audio else ''}
                for q in m.questions.all()
            ]
        } for m in materials]),
        'interval': request.session.get('practice_interval'),  # ✅ 补上这行
    })

@login_required
def review_page(request):
    """
    根据练习模式显示不同的验收页：
    - A 模式：键盘输入验收页
    - B 模式：手写记录验收页
    - C 模式：口述回答验收页
    """
    session_id = request.session.get('current_session_id')
    session_obj = PracticeSession.objects.filter(id=session_id).first()

    if not session_obj:
        return redirect('home')  # ✅ 防止 session 为空时报错

    mode = session_obj.mode

    if request.method == 'POST':
        if mode in ['A', 'B']:
            for material in Material.objects.all():
                user_input = request.POST.get(f'input_{material.id}', '')
                result = request.POST.get(f'result_{material.id}', None)
                if result:
                    is_correct = (result == 'correct')
                    AnswerRecord.objects.create(
                        user=request.user,
                        material=material,
                        session=session_obj,
                        user_input=user_input,
                        is_correct=is_correct
                    )
        else:
            # C 模式（已创建 AnswerRecord，只更新结果）
            for rec in AnswerRecord.objects.filter(session=session_obj, user=request.user):
                val = request.POST.get(f'result_{rec.id}', None)
                if val == 'correct':
                    rec.is_correct = True
                elif val == 'wrong':
                    rec.is_correct = False
                rec.save()

        request.session.pop('current_session_id', None)
        return redirect('home')  # ✅ 仅 POST 提交完毕后跳转

    # GET：取出本轮答题记录
    records = AnswerRecord.objects.filter(session=session_obj, user=request.user).select_related('material')

    wrong_counts = {}
    for rec in records:
        mid = rec.material.id
        if mid not in wrong_counts:
            wrong_counts[mid] = AnswerRecord.objects.filter(
                material=rec.material,
                user=request.user,
                is_correct=False
            ).count()

    # ✅ 根据模式选择模板
    if mode == 'A':
        template = 'dictation/review_page_A.html'
    elif mode == 'B':
        template = 'dictation/review_page_B.html'
    else:
        template = 'dictation/review_page_C.html'

    return render(request, template, {
        'records': records,
        'session': session_obj,
        'wrong_counts': wrong_counts
    })

@login_required
def api_material(request, pk):
    material = Material.objects.get(pk=pk)
    question = material.questions.first()
    wrong_count = AnswerRecord.objects.filter(material=material, is_correct=False).count()
    return JsonResponse({
        'id': material.id,
        'content': material.content,
        'audio': material.audio.url if material.audio else '',
        'question_text': question.question_text if question else '',
        'question_audio': question.question_audio.url if question and question.question_audio else '',
        'wrong_count': wrong_count
    })

@login_required
def answer_record_list(request):
    records = AnswerRecord.objects.select_related('material').prefetch_related('material__categories')

    category_id = request.GET.get('category')
    if category_id:
        records = records.filter(material__categories__id=category_id)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        records = records.filter(created_at__date__gte=parse_date(start_date))
    if end_date:
        records = records.filter(created_at__date__lte=parse_date(end_date))

    records = records.order_by('-created_at')
    categories = Category.objects.all()
    paginator = Paginator(records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dictation/answer_history.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_id,
        'start_date': start_date,
        'end_date': end_date,
    })

@login_required
def session_history(request):
    sessions = PracticeSession.objects.filter(user=request.user).order_by('-created_at')

    category_id = request.GET.get('category')
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')

    if category_id:
        sessions = sessions.filter(answerrecord__material__categories__id=category_id).distinct()
    if start:
        sessions = sessions.filter(created_at__date__gte=parse_date(start))
    if end:
        sessions = sessions.filter(created_at__date__lte=parse_date(end))

    categories = Category.objects.all()
    paginator = Paginator(sessions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dictation/session_history.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_id,
        'start_date': start,
        'end_date': end,
    })

@login_required
def review_wrong_list(request):
    wrong_materials = Material.objects.annotate(
        wrong_count=Count('answerrecord', filter=Q(answerrecord__is_correct=False))
    ).filter(wrong_count__gt=0)
    return render(request, 'dictation/wrong_list.html', {'materials': wrong_materials})


@csrf_exempt
def retry_wrong(request):
    if request.method == 'POST':
        wrong_materials = Material.objects.annotate(
            wrong_count=Count('answerrecord', filter=Q(answerrecord__is_correct=False))
        ).filter(wrong_count__gt=0)

        wrong_ids = list(wrong_materials.values_list('id', flat=True))
        if not wrong_ids:
            return redirect('review_wrong_list')

        request.session['practice_material_ids'] = wrong_ids
        request.session['practice_interval'] = 3
        request.session['practice_mode'] = 'A'
        return redirect('practice_play')

@login_required
def material_list(request):
    materials = Material.objects.all().order_by('-id')
    paginator = Paginator(materials, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'dictation/material_list.html', {'page_obj': page_obj})

@login_required
def edit_material(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES, instance=material)
        formset = QuestionFormSet(request.POST, request.FILES, instance=material, prefix='question_set')
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('material_list')
    else:
        form = MaterialForm(instance=material)
        formset = QuestionFormSet(instance=material, prefix='question_set')
    return render(request, 'dictation/edit_material.html', {'form': form, 'formset': formset, 'material': material})

@login_required
def delete_material(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        material.delete()
        return redirect('material_list')
    return render(request, 'dictation/delete_material_confirm.html', {'material': material})

@login_required
def session_detail(request, pk):
    session = get_object_or_404(PracticeSession, pk=pk)
    records = AnswerRecord.objects.filter(session=session).select_related('material')

    total = records.count()
    correct = records.filter(is_correct=True).count()
    correct_rate = round((correct / total) * 100, 1) if total else 0

    return render(request, 'dictation/session_detail.html', {
        'session': session,
        'records': records,
        'correct_rate': correct_rate,
    })

@csrf_exempt
@login_required
def retry_session(request, pk):
    session = get_object_or_404(PracticeSession, pk=pk)
    # 找出该次练习使用的材料 ID 顺序
    records = AnswerRecord.objects.filter(session=session).order_by('id')
    material_ids = list(records.values_list('material_id', flat=True).distinct())
    random.shuffle(material_ids)

    if not material_ids:
        return redirect('session_detail', pk=pk)

    # ✅ 判断用户是否勾选了“打乱顺序”
    if request.method == 'POST' and request.POST.get('shuffle') == 'on':

    # ✅ 打乱材料播放顺序
        random.shuffle(material_ids)

    # 写入 session
    request.session['practice_material_ids'] = material_ids
    request.session['practice_interval'] = session.interval
    request.session['practice_mode'] = session.mode

    return redirect('practice_play')

@csrf_exempt
def api_save_answer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        material_id = data.get('material_id')
        recognized_text = data.get('recognized_text')
        base64audio = data.get('base64audio')
        auto_judge = data.get('auto_judge')

        user = request.user if request.user.is_authenticated else None
        material = Material.objects.get(pk=material_id)
        # 你可以在 practice_play 中存 session_id
        session_id = request.session.get('current_session_id')
        session_obj = PracticeSession.objects.get(id=session_id) if session_id else None

        # 创建答题记录
        AnswerRecord.objects.create(
            user=user,
            session=session_obj,
            material=material,
            user_input=recognized_text,
            is_correct=auto_judge,
            audio_data=base64audio
        )
        return JsonResponse({"message": "OK"})
    return JsonResponse({"error": "GET not allowed"}, status=405)
