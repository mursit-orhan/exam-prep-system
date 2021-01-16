from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile
from .models import Certificate, Question, Option, Quiz, Course, Chapter, QuizExam, StudentAnswer
import nested_admin


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'is_student', 'is_staff', 'is_admin')
    list_filter = ('is_admin','is_student')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_admin', 'is_staff', 'is_student')}),
    )
    # add_form = forms.UserCreationForm
    # form = forms.UserChangeForm

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        })
    )

    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


class UserProfileAdmin(admin.ModelAdmin):
    pass


class CertificateAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    fields = ('name', 'description')


class OptionInline(nested_admin.NestedTabularInline):
    model = Option
    extra = 4
    max_num = 4


class QuestionInline(nested_admin.NestedTabularInline):
    model = Question
    inlines = [OptionInline,]
    extra = 5


class QuizAdmin(nested_admin.NestedModelAdmin):
    inlines = [QuestionInline, ]


class StudentAnswerInline(nested_admin.NestedTabularInline):
    model = StudentAnswer


class QuizExamAdmin(nested_admin.NestedModelAdmin):
    inlines = [StudentAnswerInline, ]


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Certificate, CertificateAdmin)
admin.site.register(Course)
admin.site.register(Chapter)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(QuizExam, QuizExamAdmin)
admin.site.register(StudentAnswer)

