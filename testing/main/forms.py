from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, TextInput
from .models import *


#
#
class RegisterUserForms(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'from-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'from-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'from-input'}))
    full_name = forms.CharField(label='ФИО', max_length=100)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'full_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'from-input'}),
            'password1': forms.PasswordInput(attrs={'class': 'from-input'}),
            'password2': forms.PasswordInput(attrs={'class': 'from-input'}),
            'full_name': forms.TextInput(attrs={'class': 'from-input'}),

        }


class VoprosForm(forms.ModelForm):
    class Meta:
        model = VOPROS
        fields = ["IND", 'QUESTION', 'OTVETS', 'TRUE_OTVET']
        widgets = {
            'QUESTION': forms.Textarea(attrs={'rows': 3}),
            'IND': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'nons', 'hidden': True, }),
            'IND': forms.HiddenInput(attrs={'label': False}),

        }
        attrs = {'class': 'form-style'}
        required = {
            'OTVETS': False,
        }


class Vopros_NameForm(forms.ModelForm):
    class Meta:
        model = VOPROS_NAME
        fields = ['NAME', 'LENGHT_VOPROS', "BALL", "HP", "BLOCK"]
        widgets = {
            'BLOCK': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'nons', 'hidden': True, }),
            'BLOCK': forms.HiddenInput(attrs={'label': False}),
        }
        attrs = {'class': 'form-style'}


class BLOCK_FORM(forms.ModelForm):
    class Meta:
        model = BLOCK
        fields = ['NAME']


class GUIDE_FORM(ModelForm):
    class Meta:
        model = GUIDE_MODEL
        fields = ['NAME', 'TEXT', 'LINK', 'description', 'photo']
        widgets = {
            'NAME': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название'}),
            'TEXT': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Описание'}),
            'LINK': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ссылка на ресурс'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Описание'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }


class NumberForm(forms.Form):
    number = forms.IntegerField(label='Введите число')


class TZ_FORM(ModelForm):
    class Meta:
        model = TZ
        fields = ["name", 'text', "photo", "document"]


class TZ_ANSWER_FORM(forms.ModelForm):
    class Meta:
        model = TZ_ANSWER
        fields = ['text', 'document']


class CreatePollForm(forms.ModelForm):
    choices = forms.CharField(widget=forms.Textarea, help_text='Введите варианты ответов, разделенные новой строкой.')

    class Meta:
        model = Question
        fields = ['question_text']

    def save(self, commit=True):
        question = super().save(commit=commit)
        choices = self.cleaned_data['choices'].split('\n')
        for choice_text in choices:
            Choice.objects.create(question=question, choice_text=choice_text)
        return question
class PollResponseForm(forms.Form):
    choice = forms.ModelChoiceField(queryset=Choice.objects.none())

    def __init__(self, *args, poll=None, **kwargs):
        super(PollResponseForm, self).__init__(*args, **kwargs)
        self.fields['choice'].queryset = poll.choice_set.all()