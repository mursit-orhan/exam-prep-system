from django.shortcuts import render
from django.http.response import HttpResponse
import requests
from . import forms


def index(request):
    """View function for home page of site."""
    response = requests.get('http://127.0.0.1:8000/api/summary')
    summary = response.json()
    return render(request, 'index.html', context=summary)


def courses(request):
    response = requests.get('http://127.0.0.1:8000/api/courses')
    course_list = response.json()
    context = {'course_list': course_list}
    return render(request, 'course_list.html', context)


def course_detail(request, course_id):
    response = requests.get('http://127.0.0.1:8000/api/courses/' + str(course_id) + "/")
    course = response.json()
    # response = requests.get('http://127.0.0.1:8000/api/chapters/?course_id' + str(course_id))
    # chapter_list = response.json()
    context = {'course': course}
    return render(request, 'api_client/course_detail.html', context)


def chapter_detail(request, chapter_id):
    print("chapter id", chapter_id)
    token = request.session.get('token')
    is_authenticated = False
    if token:
        is_authenticated = True
    headers = {'Authorization': 'Token {}'.format(request.session.get('token'))}
    response = requests.get('http://127.0.0.1:8000/api/chapters/' + str(chapter_id) + "/", headers=headers)
    chapter = response.json()
    context = {'chapter': chapter, 'is_authenticated': is_authenticated}
    print(context)
    return render(request, 'api_client/chapter_detail.html', context)


def quiz_detail(request, quiz_id):
    response = requests.get('http://127.0.0.1:8000/api/quizzes/' + str(quiz_id) + '/')

    quiz = response.json()
    context = {'quiz': quiz}
    return render(request, 'api_client/quiz_detail.html', context)


from django.shortcuts import redirect


def login(request):
    if request.method == 'POST':
        response = requests.post('http://127.0.0.1:8000/api/login/', data=request.POST).json()
        print(response)
        token = response.get('token')
        if token:
            request.session['token'] = token
            user = response.get('user')
            user['is_authenticated'] = True
            request.session['user'] = user
            return redirect('/')
        form = forms.UserAuthenticationForm(response)
    else:
        form = forms.UserAuthenticationForm()
    context = {'form': form}
    return render(request, 'api_client/login.html', context)


def logout(request):
    request.session.pop('token')
    request.session.pop('user')
    return redirect('/')


def submit_quiz(request, quiz_id):
    print(request.POST)
    token = request.session.get('token')
    is_authenticated = False
    if token:
        is_authenticated = True
    data = request.POST
    user = request.session['user']

    headers = {'Authorization': 'Token {}'.format(request.session.get('token'))}
    quiz_exam_data = {'student': user['id'], 'quiz': quiz_id }
    response = requests.post('http://127.0.0.1:8000/api/quiz_exam/',
                             data=quiz_exam_data,
                             headers=headers)
    quiz_exam = response.json()
    print(quiz_exam)
    data_answer_post = []
    for key, value in data.items():
        if 'question' in key:
            data_answer_post.append({'quiz_exam': quiz_exam['id'], 'question': key.replace('question', ''), 'answer': value[0]})

    print("data answer post ", data_answer_post)
    for data in data_answer_post:
        response = requests.post('http://127.0.0.1:8000/api/student_answer/',
                             data=data,
                             headers=headers)
        quiz = response.json()

    response = requests.get('http://127.0.0.1:8000/api/quizzes/' + str(quiz_id) + '/', headers=headers)
    quiz_data = response.json()
    quiz_exam_id = str(quiz_exam['id'])
    response = requests.get('http://127.0.0.1:8000/api/quiz_exam/' + quiz_exam_id + '/', headers=headers)
    quiz_exam_data = response.json()
    quiz_data['total'] = len(quiz_exam_data['studentanswer_set'])
    quiz_data['correct'] = quiz_exam_data['score']
    quiz_data['wrong'] = quiz_data['total'] - quiz_data['correct']
    context = {'quiz': quiz_data}
    return render(request, 'api_client/quiz_result.html', context)

