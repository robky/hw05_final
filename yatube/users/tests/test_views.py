from http import HTTPStatus

from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.tests.factorys import UserFactory


class UserPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.data_correct_form = (
            ('users:login', {
                'username': forms.fields.CharField,
                'password': forms.fields.CharField,
            }),
            ('users:password_change', {
                'old_password': forms.fields.CharField,
                'new_password1': forms.fields.CharField,
                'new_password2': forms.fields.CharField,
            }),
            ('users:password_change_done', {}),
            ('users:password_reset', {'email': forms.fields.EmailField, }),
            ('users:password_reset_done', {}),
            ('users:signup', {
                'first_name': forms.fields.CharField,
                'last_name': forms.fields.CharField,
                'username': forms.fields.CharField,
                'email': forms.fields.EmailField,
            }),
            ('users:logout', {},)
        )

    def setUp(self):
        self.user = UserFactory.create()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_page_show_correct_context(self):
        for address, values in self.data_correct_form:
            response = self.authorized_client.get(reverse(address))
            self.assertEqual(response.status_code, HTTPStatus.OK)
            for value, expected in values.items():
                with self.subTest(adress=address, value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)
