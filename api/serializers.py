from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from . import models

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        fields = ('id', 'email')

    def validate(self, attrs):
        user = authenticate(**attrs)
        if user:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('id', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = models.User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('id', 'email', 'password')


class StudentQuizListSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Quiz
        fields = ('id', 'title', 'description', 'slug', 'questions_count', 'completed', 'score', 'progress')
        read_only_fields = ('questions_count', 'completed', 'score', 'progress')

    def get_completed(self, obj):
        try:
            quiz_exam = models.QuizExam.objects.get(user=self.context['request'].user, quiz=obj)
            return quiz_exam.completed
        except models.QuizExam.DoesNotExist:
            return None

    def get_progress(self, obj):
        try:
            quiz_exam = models.QuizExam.objects.get(user=self.context['request'].user, quiz=obj)

            if not quiz_exam.completed:
                questions_answered = models.StudentAnswer.objects.filter(quiz_exam=quiz_exam, answer__isnull=False).count()
                total_questions = obj.question_set.all().count()
                return int(questions_answered/total_questions)
            return None
        except models.QuizExam.DoesNotExist:
            return None

class QuizListSerializer(serializers.ModelSerializer):
    questions_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Quiz
        fields = ('id', 'title', 'description', 'questions_count')
        read_only_fields = ('questions_count',)

    def get_questions_count(self, obj):
        return obj.question_set.all().count()


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Option
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    option_set = OptionSerializer(many=True)

    class Meta:
        model = models.Question
        fields = '__all__'


class QuizDetailSerializer(serializers.ModelSerializer):
    # quiz_exam_set = serializers.SerializerMethodField()
    question_set = QuestionSerializer(many=True)

    class Meta:
        model = models.Quiz
        fields = '__all__'

    # def get_quiz_exam_set(self, obj):
    #     try:
    #         user = self.context['request'].user
    #         print(user)
    #         quiz_exam = models.QuizExam.objects.get(student=self.context['request'].user, quiz=obj)
    #         serializer = QuizExamSerializer(quiz_exam)
    #         return serializer.data
    #     except models.QuizExam.DoesNotExist:
    #         return None


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StudentAnswer
        fields = '__all__'


class QuizExamSerializer(serializers.ModelSerializer):
    studentanswer_set = StudentAnswerSerializer(many=True, required=False)

    class Meta:
        model = models.QuizExam
        fields = '__all__'


class ChapterSerializer(serializers.ModelSerializer):
    quiz_set = QuizListSerializer(many=True)

    class Meta:
        model = models.Chapter
        fields = ('id', 'title', 'description', 'quiz_set')


class CourseSerializer(serializers.ModelSerializer):
    chapter_set = ChapterSerializer(many=True, required=False)

    class Meta:
        model = models.Course
        fields = ('id', 'title', 'description', 'chapter_set')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 4}}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


