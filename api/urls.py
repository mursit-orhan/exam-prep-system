from django.urls import path, include, re_path
from rest_framework import routers
from . import views
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register('users', views.UserViewSet)
router.register('courses', views.CourseViewSet)
router.register('chapters', views.ChapterViewSet)
router.register('quiz_exam', views.QuizExamViewSet)
router.register('student_answer', views.StudentAnswer)




urlpatterns = router.urls

urlpatterns += [
    path('summary', views.summary, name="summary"),
    path('quizzes', views.QuizListAPI.as_view(), name="quizzes"),
    re_path(r'quizzes/(?P<slug>[\w\-]+)/$>', views.QuizDetailView.as_view(), name="quiz_detail"),
    path('quizzes/<int:pk>/', views.QuizDetailView.as_view(), name="quiz_detail"),
    path('save_answer', views.StudentAnswerSaver.as_view())
    # path('snippets/<int:pk>/', views.SnippetDetail.as_view()),
]


urlpatterns += [
    path('login/', views.LoginAPI.as_view()),
    path('register/', views.RegisterAPI.as_view()),
    path('user/', views.UserAPI.as_view()),
]
urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


