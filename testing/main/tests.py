# main/tests.py

from django.test import TestCase
from django.urls import reverse
from .models import User_Score

class RegisterViewTests(TestCase):
    def test_register_view_success(self):
        # Подготовка данных для отправки POST-запроса
        data = {
            'username': 'testuser',
            'full_name': 'Test User',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }

        # Отправка POST-запроса на ваше представление регистрации
        response = self.client.post(reverse('register'), data)

        # Проверка, что пользователь был создан успешно
        self.assertEqual(response.status_code, 302)  # Ожидаем перенаправление после успешной регистрации
        self.assertTrue(User_Score.objects.filter(name='testuser').exists())

    def test_register_view_failure(self):
        # Подготовка неверных данных для отправки POST-запроса
        data = {
            'username': '',  # Это поле обязательное, так что оставляем пустым
            'full_name': 'Test User',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }

        # Отправка POST-запроса на ваше представление регистрации
        response = self.client.post(reverse('register'), data)

        # Проверка, что пользователь не был создан из-за ошибок валидации
        self.assertEqual(response.status_code, 200)  # Ожидаем успешный ответ, так как валидация формы не прошла
        self.assertFalse(User_Score.objects.filter(name='testuser').exists())
