from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core import validators
from . import utils
from django.conf import settings

from taggit.managers import TaggableManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(email=self.normalize_email(email))

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password
        )
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class StudentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_student=True)


class TeacherManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_teacher=True)


class User(AbstractBaseUser):
    email = models.EmailField(_('email address'),  max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_student = models.BooleanField(default=True)
    # is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    # students = StudentManager()
    # teachers = TeacherManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

LEVELS = (
        ('b', 'Basic'),
        ('a', 'Advance'),
    )


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='profile-images')

    level = models.CharField(
        max_length=1,
        choices=LEVELS,
        blank=True,
        default='b',
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Certificate(utils.TimeStampModelMixin, models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()


class Course(utils.TimeStampModelMixin, models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title


class Chapter(utils.TimeStampModelMixin, models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    level = models.CharField(
        max_length=1,
        choices=LEVELS,
        blank=True,
        default='b',
    )
    media_url = models.CharField(max_length=100)
    is_published = models.BooleanField(default=False)
    image = models.ImageField(upload_to='thumbnails/')
    rating = models.PositiveSmallIntegerField(
        validators=[
            validators.MinValueValidator(0),
            validators.MaxValueValidator(5)],
        default=range(1, 6)
    )
    course = models.ForeignKey(Course, related_name='chapter_set', on_delete=models.SET_NULL, null=True)

    def preview(self):
        url = self.media_url
        url = url.replace("https://www.youtube.com/watch?v", "http://www.youtube.com/embeded/")
        return url

    def __str__(self):
        return self.title


class Quiz(utils.TimeStampModelMixin, models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(blank=True)
    is_published = models.BooleanField(default=False)
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.title


class Question(utils.TimeStampModelMixin, models.Model):
    description = models.CharField(max_length=200)
    questioneer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='questions', on_delete=models.SET_NULL, null=True)
    level = models.CharField(
        max_length=1,
        choices=LEVELS,
        blank=True,
        default='b',
    )
    # assignments = models.ManyToManyField(Assignment)
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True)
    tags = TaggableManager()

    def __str__(self):
        return self.description


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.description


class QuizExam(utils.TimeStampModelMixin, models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return 'student={}, quiz={}'.format(self.student, self.quiz)


class StudentAnswer(models.Model):
    quiz_exam = models.ForeignKey(QuizExam, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Option, on_delete=models.CASCADE, null=True)

# @receiver(pre_save, sender=Quiz)
# def slugify_name(sender, instance, *args, **kwargs):
#     instance.slug = slugify(instance.title)