from datetime import datetime

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import FormView
from django.contrib.auth.forms import AuthenticationForm
import json

from .forms import *
from .models import *

from django.forms import modelformset_factory, formset_factory, model_to_dict
from django.shortcuts import redirect, render
from .forms import VoprosForm, Vopros_NameForm
from .models import VOPROS


# Главная
def index(request):
    if request.user.is_authenticated:
        info = BLOCK.objects.all()
        return render(request, 'main/index.html', {'title': 'Главная страница', 'info': info})
    else:
        return redirect("login")


def Infor(request):
    return render(request, 'main/Infor.html')

# Смотрим какие тесты надо отобразитьь в блоке
def block(request, pk):
    if request.user.is_authenticated:
        test_names = [test.NAME for test in VOPROS_NAME.objects.filter(BLOCK=pk)]

        test_names_in_results = TestResult.objects.values_list('test_name', flat=True).filter(
            user_name=request.user.username).distinct()
        test_names_not_in_results = set(test_names) - set(test_names_in_results)
        test_objects_not_in_results = VOPROS_NAME.objects.filter(NAME__in=test_names_not_in_results, BLOCK=pk)
        test_results = TestResult.objects.filter(user_name=request.user.username)
        user_hp = {}
        for test in test_objects_not_in_results:
            vopros_names = VOPROS_NAME.objects.filter(NAME=test.NAME, BLOCK=pk)
            if vopros_names.exists():
                user_hp[test.NAME] = vopros_names.first().HP

        for test in test_names_in_results:
            if TestResult.objects.filter(user_name=request.user.username, test_name=test).exists():
                test_result = TestResult.objects.get(user_name=request.user.username, test_name=test)
                if test_result.hp > 0:
                    test_objects_not_in_results |= VOPROS_NAME.objects.filter(NAME=test, BLOCK=pk)
                    user_hp[test] = TestResult.objects.filter(user_name=request.user.username,
                                                              test_name=test).values_list(
                        'hp', flat=True).first()

            else:
                vopros_name = VOPROS_NAME.objects.get(NAME=test)
                if vopros_name.HP > 0:
                    test_objects_not_in_results |= VOPROS_NAME.objects.filter(NAME=test, BLOCK=pk)
                    user_hp[test] = TestResult.objects.filter(user_name=request.user.username,
                                                              test_name=test).values_list(
                        'hp', flat=True).first()

        US_HP = []
        for test in test_objects_not_in_results:
            US_HP.append({"NAME": test, "HP": user_hp[test.NAME]})

        context = {
            'title': 'Главная страница',
            'test': US_HP,
            "block_name": pk

        }
        return render(request, 'main/block.html', context)
    else:
        return redirect("login")

# Новый блок
def new_block(request):
    if request.method == 'POST':
        form = BLOCK_FORM(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = BLOCK_FORM()
    return render(request, 'main/new_block.html', {'title': 'Новый справочник', 'form': form})

# страница со всеми справочниками
def guide(request):
    info = GUIDE_MODEL.objects.all()
    return render(request, 'main/guide.html', {'title': 'Справочник', 'info': info})


# РЕзультаты для адмена
def result(request):
    if request.user.is_superuser:

        test_results = REZ.objects.all()[::-1]
        tz_result = TZ_ANSWER.objects.all()[::-1]
        return render(request, 'main/result.html',
                      {'title': 'Результаты', "result1": test_results, "result2": tz_result})

    elif request.user.is_authenticated:

        test_results = TestResult.objects.filter(user_name=request.user.username)
        tz_result = TZ_ANSWER.objects.filter(user=request.user.username, FLAG=1)

        return render(request, 'main/result.html',
                      {'title': 'Результаты', "result1": test_results, "result2": tz_result})
    else:
        return redirect("login")


# Прохождение тесты
def test(request, pk):
    if request.user.is_authenticated:
        vopros_list = VOPROS.objects.filter(IND=pk)
        question = VOPROS_NAME.objects.filter(id=pk)
        name_test = model_to_dict(question[0])["NAME"]
        QUESTION = []
        OTVETS = []
        TRUE_OTVET = []
        for vopros in vopros_list:
            QUESTION.append(model_to_dict(vopros)["QUESTION"])
            OTVETS.append(model_to_dict(vopros)["OTVETS"].split("\r\n"))
            TRUE_OTVET.append(model_to_dict(vopros)["TRUE_OTVET"].split(" "))

        my_dict = dict()
        for i in range(len(QUESTION)):
            my_dict[QUESTION[i]] = OTVETS[i]
        if request.method == 'POST':
            i = 0
            score = 0
            for question, options in my_dict.items():
                selected_options = request.POST.getlist(question + '[]')
                if (selected_options == TRUE_OTVET[i]):
                    score += 1
                i += 1
            question = VOPROS_NAME.objects.get(id=pk)
            ball = question.BALL
            try:
                test_result = TestResult.objects.get(user_name=request.user.username, test_name=name_test)
                hp = test_result.hp
                ball_old = test_result.ball

            except TestResult.DoesNotExist:
                hp = question.HP
                ball_old = 0
            new_ball = ball * (round(score / len(TRUE_OTVET) * 100, 2)) / 100
            if ball_old > new_ball:
                pass
            elif new_ball == 0 and ball_old == 0:
                TestResult.objects.update_or_create(
                    user_name=request.user.username,
                    test_name=name_test,
                    defaults={
                        'score': round(score / len(TRUE_OTVET) * 100, 2),
                        'ball': 0,
                        'hp': hp - 1,
                    }
                )
            else:
                TestResult.objects.update_or_create(
                    user_name=request.user.username,
                    test_name=name_test,
                    defaults={
                        'score': round(score / len(TRUE_OTVET) * 100, 2),
                        'ball': new_ball,
                        'hp': hp - 1,
                    }
                )

            user_score, created = User_Score.objects.get_or_create(name=request.user.username)
            user_score.score += int(new_ball - ball_old)
            user_score.save()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if int(new_ball - ball_old) > 0:
                rez = REZ(name=request.user.username, test_name=name_test, full_name=user_score.full_name,
                          score=int(new_ball - ball_old), date=now, ball=ball)
                rez.save()
            messages.success(request,
                             'Тест пройден смотрите в результатах')  # Добавление сообщения об успешной отправке

            return redirect('home')
        return render(request, 'main/test.html', {'question_data': my_dict, "pk": pk})
    else:
        return redirect("login")




# Сохраняем результаты
def save_result(request, correct_answers, alls, ind):
    print(request.user, (correct_answers / alls) * 100, ind)
    return redirect('home')


# Регистрация
class RegisterFormView(FormView):
    form_class = RegisterUserForms

    template_name = 'main/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        form.save()
        full_name = form.cleaned_data['full_name']

        user = User_Score.objects.create(name=username, full_name=full_name, score=0)
        user.save()
        return super(RegisterFormView, self).form_valid(form)

    def form_invalid(self, form):
        return super(RegisterFormView, self).form_invalid(form)


# Авторизация
class LoginUser(LoginView):
    form_class = AuthenticationForm

    template_name = 'main/login.html'

    def form_valid(self, form):
        return super(LoginUser, self).form_valid(form)

    def form_invalid(self, form):
        return super(LoginUser, self).form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('home')


# Выход пользователя
def LogoutUser(request):
    logout(request),
    return redirect('login')

# НОвый спрвочник страница создания
def new_guide(request):
    if request.method == 'POST':
        form = GUIDE_FORM(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('guide')
    else:
        form = GUIDE_FORM()
    return render(request, 'main/new_guide.html', {'title': 'Новый справочник', 'form': form})


from django.shortcuts import render, redirect, get_object_or_404
from .models import GUIDE_MODEL
from .forms import GUIDE_FORM

#Справочник удалсить
def delete_guide(request, guide_id):
    # Получаем объект справочника по его id

    guide = get_object_or_404(GUIDE_MODEL, pk=guide_id)

    if request.method == 'POST':
        # Если метод запроса POST, то удаляем справочник
        guide.delete()
        return redirect('guide')

# Обновление справочника
def edit_guide(request, pk):
    guide = get_object_or_404(GUIDE_MODEL, pk=pk)

    if request.method == 'POST':
        form = GUIDE_FORM(request.POST, request.FILES, instance=guide)
        if form.is_valid():
            form.save()
            return redirect('guide')
    else:
        form = GUIDE_FORM(instance=guide)

    return render(request, 'main/new_guide.html', {'title': 'Редактирование справочника', 'form': form})

# Справочник Блок тестов
def delete_block(request, guide_id):
    # Получаем объект справочника по его id
    test = get_object_or_404(BLOCK, pk=guide_id)

    if request.method == 'POST':
        # Если метод запроса POST, то удаляем справочник
        test.delete()
        return redirect('home')
    else:
        # Иначе, отображаем страницу подтверждения удаления
        return render(request, 'main/delete_guide.html', {'title': 'Удалить справочник', 'guide': guide})

#Страница вопросов
def my_vopros(request, test_id):
    form = VoprosForm(request.POST or None)
    form.fields['IND'].initial = test_id
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'main/create_vopros.html', {'title': 'Новый вопрос', 'form': form})


#Создание вопросов для теста
def create_question(request, N, ind):
    MyFormSet = formset_factory(VoprosForm, extra=0)

    if request.method == 'POST':
        formset = MyFormSet(request.POST, initial=[{'IND': ind}] * N)
        if formset.is_valid():
            for form in formset:
                form.save()
            return redirect('home')
    else:
        formset = MyFormSet(initial=[{'IND': ind}] * N)

    return render(request, 'main/create_vopros.html', {'formset': formset})

    # 'IND': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'nons', 'hidden': True, }),
    # 'IND': forms.HiddenInput(attrs={'label': False}),

# Новый тест-имя
def new_question(request, ind):
    form = Vopros_NameForm(initial={'BLOCK': ind})
    if request.method == 'POST':
        form = Vopros_NameForm(request.POST, initial={'BLOCK': ind})
        if form.is_valid():
            instance = form.save(commit=False)
            form_value = int(request.POST.get('LENGHT_VOPROS'))
            instance.save()
            saved_id = instance.id
            return redirect(f'/vopros/{form_value}/{saved_id}/')
    return render(request, 'main/create_test.html', {'title': 'Новый вопрос', 'form': form})

#Рейтинг
def rating(request):
    if request.user.is_authenticated:

        # Получаем первые 5 пользователей, отсортированных по score по убыванию
        try:
            top_users = User_Score.objects.order_by('-score')[:5]

            # Получаем текущий score пользователя
            current_user_score = User_Score.objects.get(name=request.user.username).score

            # Извлекаем все score из топ-5 пользователей
            top_scores = [user.score for user in top_users]

            # Если текущий пользователь входит в топ-5, выводим его позицию в списке
            if current_user_score in top_scores:
                current_user_position = top_scores.index(current_user_score) + 1
                current_user = User_Score.objects.get(name=request.user.username)
                current_user.position = current_user_position
                current_user.save()
            else:
                all_users = User_Score.objects.order_by('-score')
                current_user_position = User_Score.objects.filter(score__gt=current_user_score).count() + 1

            # Создаем контекст для передачи в шаблон
            context = {
                'top_users': top_users,
                'current_user_position': current_user_position,
                "posit": [1, 2, 3, 4, 5]
            }
        except:
            context = {}
            pass
        return render(request, 'main/Rating.html', context)
    else:
        return redirect('login')

#Удалить тест
def DELIT(request, pk):
    test = get_object_or_404(VOPROS_NAME, pk=pk)

    if request.method == 'POST':
        # Если метод запроса POST, то удаляем справочник
        test.delete()
        return redirect('home')
    else:
        # Иначе, отображаем страницу подтверждения удаления
        return render(request, 'main/delete_guide.html', {'title': 'Удалить справочник', 'guide': guide})

# Просмотр справочника внутри
def guide_detail(request, pk):
    guide = get_object_or_404(GUIDE_MODEL, pk=pk)
    context = {'guide_obj': guide}
    return render(request, 'main/guide_info.html', context)


from django.db.models import Q

#Отображаем задания в зависимости от того выполнено ли оно
@login_required
def TZ_F(request):
    solved_tasks = TZ_ANSWER.objects.filter(user=request.user.username, FLAG__in=[3, 2]).values_list('id_tz', flat=True)
    info = TZ.objects.exclude(id__in=solved_tasks)
    tz_answers = TZ_ANSWER.objects.filter(user=request.user.username, FLAG__in=[2, 3])
    context = {
        'title': 'ЗАДАНИЯ',
        'info': info,
        'tz_answers': tz_answers,
    }
    return render(request, 'main/tz.html', context)

# Создание задания
def new_tz(request):
    if request.method == 'POST':
        form = TZ_FORM(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('TZ')
    else:
        form = TZ_FORM(request.POST, request.FILES)
    return render(request, 'main/new_tz.html', {'title': 'Новое задание', 'form': form})

# Отображение задания
def tz_detail(request, pk):
    tz = get_object_or_404(TZ, pk=pk)
    context = {'guide': tz}
    return render(request, 'main/tz_info.html', context)

#Удаление задания
def delete_tz(request, pk):
    test = get_object_or_404(TZ, id=pk)

    if request.method == 'POST':
        # Если метод запроса POST, то удаляем справочник
        test.delete()
        return redirect("TZ")
    else:
        # Иначе, отображаем страницу подтверждения удаления
        return redirect("TZ")

# Ответ на задание
def answer_tz(request, pk):
    tz = get_object_or_404(TZ, id=pk)

    tz_answer = TZ_ANSWER.objects.filter(id_tz=pk, user=request.user.username).first()

    if request.method == 'POST':
        form = TZ_ANSWER_FORM(request.POST, request.FILES, instance=tz_answer)
        if form.is_valid():
            tz_answer = form.save(commit=False)
            tz_answer.id_tz = pk
            tz_answer.name_tz = tz.name
            tz_answer.user = request.user.username
            tz_answer.name = get_object_or_404(User_Score, name=request.user.username).full_name
            tz_answer.uploaded_at = datetime.now()
            tz_answer.FLAG = 3  # Установка значения флага
            tz_answer.save()
            messages.success(request, 'Задание успешно отправлено.')  # Добавление сообщения об успешной отправке

            return redirect('TZ')
    else:
        form = TZ_ANSWER_FORM(instance=tz_answer)

    return render(request, 'main/answer_tz.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
#просмотр списка заданий
def look_tz(request, pk):
    page = get_object_or_404(TZ_ANSWER, id=pk)

    if request.method == 'POST':
        id_tz = request.POST.get('id_tz')
        submit_value = request.POST.get('submit')
        if submit_value == 'Зачёт':
            # Обработка действия "Зачёт"
            TZ_ANSWER.objects.filter(id_tz=id_tz).update(FLAG=1)
        elif submit_value == 'Незачёт':
            # Обработка действия "Незачёт"
            TZ_ANSWER.objects.filter(id_tz=id_tz).update(FLAG=2)
        return redirect('result')

    return render(request, 'main/look_tz.html', {'page': page})




# Опросы
def poll_list(request):
    polls = Question.objects.all()
    return render(request, 'main/poll_list.html', {'polls': polls})



def poll_detail(request, pk):
    poll = get_object_or_404(Question, pk=pk)
    choices = poll.choice_set.all()
    labels = [choice for choice in range(1, len(choices)+1)]
    total_votes = sum(choice.votes for choice in choices)
    user_has_voted = PollResponse.objects.filter(poll=poll, user=request.user).exists()
    can_vote = not user_has_voted
    return render(request, 'main/poll_detail.html', {'poll': poll, 'labels': labels, 'total_votes': total_votes, 'can_vote': can_vote})



#Ответ на опрос
def submit_poll(request, pk):
    poll = get_object_or_404(Question, pk=pk)
    user = request.user

    if PollResponse.objects.filter(poll=poll, user=user).exists():
        return redirect('poll_list')

    if request.method == 'POST':
        form = PollResponseForm(request.POST, poll=poll)
        if form.is_valid():
            choice = form.cleaned_data['choice']
            choice.votes += 1
            choice.save()
            PollResponse.objects.create(poll=poll, user=user)
            return redirect('poll_list')

    form = PollResponseForm(poll=poll)
    return render(request, 'main/poll_detail.html', {'poll': poll, 'form': form})

#Создание опроса
def create_poll(request):
    if request.method == 'POST':
        form = CreatePollForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('poll_list')
    else:
        form = CreatePollForm()

    return render(request, 'main/create_poll.html', {'form': form})
class CheckUsernameView(View):
    def get(self, request, *args, **kwargs):
        username = self.request.GET.get('username', None)
        data = {
            'is_taken': User.objects.filter(username=username).exists()
        }
        return JsonResponse(data)