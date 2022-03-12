from collections import namedtuple

from django.test import TestCase, Client
from http import HTTPStatus
from posts.tests.factorys import UserFactory

urls = namedtuple('urls', ['address', 'template'])


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create()

        cls.un_existing_urls = (urls('/auth/unexisting_page/', ''),)
        cls.public_urls = (
            urls('/auth/login/', 'users/login.html'),
            urls('/auth/password_reset/', 'users/password_reset_form.html'),
            urls('/auth/password_reset/done/',
                 'users/password_reset_done.html'),
            urls('/auth/reset/done/', 'users/password_reset_complete.html'),
            urls('/auth/signup/', 'users/signup.html'),
            urls('/auth/logout/', 'users/logged_out.html'),
        )
        cls.authorized_urls = (
            urls('/auth/password_reset/', 'users/password_reset_form.html'),
            urls('/auth/password_reset/done/',
                 'users/password_reset_done.html'),
            urls('/auth/reset/done/', 'users/password_reset_complete.html'),
            urls('/auth/logout/', 'users/logged_out.html'),
        )
        cls.password_change_url = '/auth/password_change/'
        cls.password_change_done = '/auth/password_change/done/'
        cls.auth_login_next_url = '/auth/login/?next='
        cls.guest_redirect_urls = (
            (cls.password_change_url,
             f'{cls.auth_login_next_url}{cls.password_change_url}'),
            (cls.password_change_done,
             f'{cls.auth_login_next_url}{cls.password_change_done}'),
        )

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def urls_exists_and_uses_correct_template(self, data_urls, client, status):
        for url in data_urls:
            with self.subTest(address=url.address):
                response = client.get(url.address)
                self.assertEqual(response.status_code, status)
                if url.template:
                    self.assertTemplateUsed(response, url.template)

    def test_urls(self):
        self.urls_exists_and_uses_correct_template(
            self.un_existing_urls, self.guest_client, HTTPStatus.NOT_FOUND)
        self.urls_exists_and_uses_correct_template(
            self.public_urls, self.guest_client, HTTPStatus.OK)
        self.urls_exists_and_uses_correct_template(
            self.authorized_urls, self.authorized_client, HTTPStatus.OK
        )

    def test_redirect_anonymous_on_auth_login(self):
        for address, redirect_url in self.guest_redirect_urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertRedirects(response, redirect_url)
