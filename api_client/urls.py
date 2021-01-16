from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'client'

urlpatterns = [
    path('', views.index, name='index'),
    path('courses/', views.courses, name='courses'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('chapters/<int:chapter_id>/', views.chapter_detail, name='chapter_detail'),
    path('quizzes', views.quiz_detail, name='quizzes'),
    path('quizzes/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quizzes/<int:quiz_id>/submit-quiz', views.submit_quiz, name='submit_quiz'),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
]
