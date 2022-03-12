from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserSignUpFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.singup_name_url = 'users:signup'

    def setUp(self):
        self.guest_client = Client()

    def test_new_user(self):
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Аникей',
            'last_name': 'Аникеев',
            'username': 'anyKey',
            'email': 'abc@def.ghi',
            'password1': 'superpuper009pass',
            'password2': 'superpuper009pass',
        }
        response = self.guest_client.post(
            reverse(self.singup_name_url),
            data=form_data,
            follow=True
        )
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
