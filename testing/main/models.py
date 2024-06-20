from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class VOPROS_NAME(models.Model):
    BLOCK = models.IntegerField("ID BLOCK")
    NAME = models.CharField('НАЗВАНИЕ ТЕСТА ', max_length=50)
    LENGHT_VOPROS = models.PositiveIntegerField("Количество вопросов")
    BALL = models.IntegerField("Количество баллов ", validators=[MinValueValidator(0)])  # добавлено новое поле BALL
    HP = models.IntegerField("Количество попыток ", validators=[MinValueValidator(1)])  # добавлено новое поле BALL

    def __str__(self):
        return self.NAME


class VOPROS(models.Model):
    IND = models.IntegerField("ID ТЕСТА")
    QUESTION = models.CharField('ВОПРОС ', max_length=150)
    OTVETS = models.TextField("Варианты ответа через", blank=True)
    TRUE_OTVET = models.CharField("Правильные ответы через", max_length=100)

    def __str__(self):
        return str(self.IND)


class GUIDE_MODEL(models.Model):
    NAME = models.CharField('ИМЯ СПРАВОЧНИКА', max_length=100)
    TEXT = models.TextField('Информация: ', max_length=5000)
    LINK = models.CharField("Идентефикатор на ютуб https://www.youtube.com/embed/", max_length=250, blank=True)
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to='guide_photos/', blank=True)  # Добавлено поле для загрузки фотографий

    def __str__(self):
        return self.NAME


class TestResult(models.Model):
    user_name = models.CharField(max_length=100)
    test_name = models.CharField(max_length=100)
    score = models.FloatField()
    ball = models.FloatField()
    hp = models.IntegerField()

    def __str__(self):
        return f"{self.user_name} - {self.test_name} - {self.score}%"


class User_Score(models.Model):
    name = models.CharField(max_length=100)
    score = models.FloatField(default=0)
    full_name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.full_name)+' - '+str(self.score)


class BLOCK(models.Model):
    NAME = models.CharField('НАЗВАНИЕ БЛОКА ', max_length=50)
    def __str__(self):
        return self.NAME


class REZ(models.Model):
    name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=100)
    test_name = models.CharField(max_length=100)
    score = models.FloatField(default=0)
    ball = models.IntegerField(blank=False)
    date = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class TZ(models.Model):
    name = models.CharField("Название задания", max_length=100)
    text = models.TextField('Задание ', max_length=5000)
    photo = models.ImageField("Добавить фото", upload_to='TZ/picture/',
                              blank=True)  # Добавлено поле для загрузки фотографий
    document = models.FileField("Добавить документ", upload_to='TZ/document/', blank=True)

    def __str__(self):
        return self.name


class TZ_ANSWER(models.Model):
    id_tz = models.IntegerField("ID задания")
    name_tz = models.CharField("Название", max_length=200)
    user = models.CharField("Пользователь", max_length=200)

    name = models.CharField("ФИО", max_length=200)
    text = models.TextField('КОМЕНТАРИИ К ЗАДАНИЮ ', max_length=5000)
    document = models.FileField("Добавить документ", upload_to='TZ/document/', blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    FLAG = models.IntegerField("ЗАЧЁТ/НЕЗАЧЁТ", default=3)

    def __str__(self):
        return self.name


class Survey(models.Model):
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)


class UserResponse(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'survey')

class Question(models.Model):
    question_text = models.CharField(max_length=200)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

class PollResponse(models.Model):
    poll = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} - {self.poll.question_text}'