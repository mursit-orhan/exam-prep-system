from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.signals import request_finished
from django.dispatch import receiver
from django.db.models.signals import pre_save
from rest_framework import viewsets
from .serializers import UserSerializer
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from . import models
from . import serializers
from rest_framework import permissions
from rest_framework import generics
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from knox.models import AuthToken
from rest_framework.authtoken.models import Token


# @receiver(request_finished)
# def after_request_finished(sender, **kwargs):
#     print("--------------------------request is done  ------------------------------------")


@receiver(pre_save, sender=User)
def new_user_registered(sender, **kwargs):
    print("----------- a new user is registered send an email to me ------------------------")


class RegisterAPI(generics.GenericAPIView):
    serializer_class = serializers.RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': serializer.data,
            'token': token.key
        })


class LoginAPI(generics.GenericAPIView):
    serializer_class = serializers.LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        user_resp = {'id': user.id, 'email': user.email}
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': user_resp,
            'token': token.key
        })


class UserAPI(generics.RetrieveAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self):
        return self.request.user


class StudentAnswerSaver(generics.GenericAPIView):
    serializer_class = serializers.StudentAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):

        quiz_exam_id = request.data['quiz_exam']
        question_id = request.data['question']
        option_id = request.data['answer']
        quiz_exam = get_object_or_404(models.QuizExam, id=quiz_exam_id)
        question = get_object_or_404(models.Question, id=question_id)
        answer = get_object_or_404(models.Option, id=option_id)

        if quiz_exam.is_completed:
            return Response({'message': 'This quiz already complete. You can not answer anymore'})
        obj = get_object_or_404(models.StudentAnswer, quiz_exam=quiz_exam, question=question)
        obj.answer = answer
        obj.save()
        return Response(self.get_serializer(obj).data)


class QuizListAPI(generics.ListAPIView):
    serializer_class = serializers.QuizListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self, *args, **kwargs):
        queryset = models.Quiz.objects.all()
        # queryset = models.Quiz.objects.filter(is_published=True)
        # /api/quizzes/?q=subject
        query = self.request.GET.get("q")

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            ).distinct()

        return queryset


class QuizDetailView(generics.RetrieveAPIView):
    serializer_class = serializers.QuizDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, *args, **kwargs):
        slug = self.kwargs.get("slug")
        if slug:
            quiz = get_object_or_404(models.Quiz, slug=slug)
        else:
            quiz = get_object_or_404(models.Quiz)
        last_question = None
        # obj, created = models.QuizExam.objects.get_or_create(student=self.request.user, quiz=quiz)
        # if created:
        #     for question in models.Quiz.objects.filter(quiz=quiz):
        #         models.StudentAnswer.objects.create(quiz_exam=obj, question=question)
        # else:
        #     last_question = models.StudentAnswer.objects.filter(quiz_exam=obj, answer__isnull=False)
        #     if last_question.count() > 0:
        #         last_question = last_question.last().question.id
        #     else:
        #         last_question = None

        return Response(self.get_serializer(quiz).data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ChapterViewSet(viewsets.ModelViewSet):
    queryset = models.Chapter.objects.all()
    serializer_class = serializers.ChapterSerializer
    permission_classes = [permissions.IsAuthenticated]


class QuizExamViewSet(viewsets.ModelViewSet):
    queryset = models.QuizExam.objects.all()
    serializer_class = serializers.QuizExamSerializer
    permission_classes = [permissions.IsAuthenticated]


class StudentAnswer(viewsets.ModelViewSet):
    queryset = models.StudentAnswer.objects.all()
    serializer_class = serializers.StudentAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        print("request.da", request.data)
        serializer = serializers.StudentAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        quiz_exam_id = request.data['quiz_exam']
        option_id = request.data['answer']
        quiz_exam = get_object_or_404(models.QuizExam, id=quiz_exam_id)
        answer = get_object_or_404(models.Option, id=option_id)
        if answer.is_correct:
            quiz_exam.score+=1
            quiz_exam.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)



from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework.decorators import api_view


@api_view(['GET', 'POST'])
def summary(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_courses = models.Course.objects.all().count()
    num_quizzes = models.Quiz.objects.all().count()
    num_questions = models.Question.objects.count()
    num_students = models.User.objects.count()
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_courses': num_courses,
        'num_quizzes': num_quizzes,
        'num_questions': num_questions,
        'num_students': num_students,
        'num_visits': num_visits,
    }

    return Response(context)
