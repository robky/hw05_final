from collections import namedtuple
from http import HTTPStatus
from django.test import TestCase, Client
from posts.tests.factorys import GroupFactory, PostFactory, UserFactory


urls = namedtuple('urls', ['address', 'template'])


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create()
        cls.author = UserFactory.create()
        cls.group = GroupFactory.create()
        cls.post = PostFactory.create(author=cls.author, group=cls.group)

        cls.un_existing_urls = (urls('/un_existing_page/', ''), )
        cls.public_urls = (
            urls('/', 'posts/index.html'),
            urls(f'/group/{cls.group.slug}/', 'posts/group_list.html'),
            urls(f'/profile/{cls.author.username}/', 'posts/profile.html'),
            urls(f'/posts/{cls.post.id}/', 'posts/post_detail.html'),
        )
        cls.create_url = '/create/'
        cls.post_edit_url = f'/posts/{cls.post.id}/edit/'
        cls.auth_login_next_url = '/auth/login/?next='
        cls.author_urls = (
            urls(cls.create_url, 'posts/create_post.html'),
            urls(cls.post_edit_url, 'posts/create_post.html'),
        )
        cls.guest_redirect_urls = (
            (cls.create_url, f'{cls.auth_login_next_url}{cls.create_url}'),
            (cls.post_edit_url,
                f'{cls.auth_login_next_url}{cls.post_edit_url}'),
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.author_client = Client()
        self.author_client.force_login(self.author)

    def urls_exists_and_uses_correct_template(self, data_url, client, status):
        for url in data_url:
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
            self.author_urls, self.author_client, HTTPStatus.OK)

    def test_redirect_anonymous_on_auth_login(self):
        for address, redirect_url in self.guest_redirect_urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertRedirects(response, redirect_url)
