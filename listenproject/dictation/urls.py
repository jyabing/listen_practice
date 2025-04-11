from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('materials/', views.material_list, name='material_list'),
    path('material/new/', views.create_material, name='create_material'),
    path('material/<int:pk>/play/', views.play_material, name='play_material'),  # 这行也放这里
    path('practice/', views.practice_setting, name='practice_setting'),
    path('practice/play/', views.practice_play, name='practice_play'),
    path('practice/review/', views.review_page, name='review_page'),
    path('api/material/<int:pk>/', views.api_material, name='api_material'),
    path('material/<int:pk>/edit/', views.edit_material, name='edit_material'),
    path('material/<int:pk>/delete/', views.delete_material, name='delete_material'),
    path('review/wrong/', views.review_wrong_list, name='review_wrong_list'),
    #path('history/', views.answer_history, name='answer_history'),
    path('review/retry/', views.retry_wrong, name='retry_wrong'),
    path('session/<int:pk>/', views.session_detail, name='session_detail'),
    path('session/<int:pk>/retry/', views.retry_session, name='retry_session'),
    path('accounts/signup/', views.signup, name='signup'),
    path('api/save_answer/', views.api_save_answer, name='api_save_answer'),
    path('history/session/', views.session_history, name='session_history'),
    path('history/record/', views.answer_record_list, name='answer_record_list'),
]