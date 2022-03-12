from http import HTTPStatus

from django.test import Client, TestCase


class CoreURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data_url_and_template_names = {
            '/none/': 'core/404.html',
        }

    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_exists_and_uses_correct_template(self):
        for address, template in self.data_url_and_template_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
                self.assertTemplateUsed(response, template)
