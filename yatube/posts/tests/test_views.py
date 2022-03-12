import shutil
import tempfile
from collections import namedtuple
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.tests.factorys import GroupFactory, PostFactory, UserFactory
from posts.views import CACHE_SEC, FIRST_SYMBOL_POST, LIMIT_POSTS

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
urls = namedtuple('urls', ['address', 'args', 'template'])


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PAGINATOR_TWO_PAGE_COUNT = 3

        cls.user = UserFactory.create()
        cls.group = GroupFactory.create()

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='test_image.gif',
            content=small_gif,
            content_type='image/gif'
        )

        posts = PostFactory.create_batch(
            LIMIT_POSTS + cls.PAGINATOR_TWO_PAGE_COUNT,
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )
        cls.post = posts[-1]

        cls.index_url = urls(
            'posts:index', None, 'posts/index.html')
        cls.follow_index_url = urls(
            'posts:follow_index', None, 'posts/follow_index.html')
        cls.post_create_url = urls(
            'posts:post_create', None, 'posts/create_post.html')
        cls.group_post_url = urls(
            'posts:group_post', (cls.group.slug,), 'posts/group_list.html')
        cls.profile_url = urls(
            'posts:profile', (cls.user,), 'posts/profile.html')
        cls.post_detail_url = urls(
            'posts:post_detail', (cls.post.id,), 'posts/post_detail.html')
        cls.post_edit_url = urls(
            'posts:post_edit', (cls.post.id,), 'posts/create_post.html')
        cls.profile_follow_url = 'posts:profile_follow'
        cls.profile_unfollow_url = 'posts:profile_unfollow'

        cls.data_correct_page = (
            (cls.index_url, {
                'title': 'Последние обновления на сайте',
                'cache_sec': CACHE_SEC,
            }),
            (cls.follow_index_url, {
                'title': 'Последние обновления на сайте по избранным авторам',
            }),
            (cls.post_create_url, {}),
            (cls.group_post_url, {
                'group': cls.group,
            }),
            (cls.profile_url, {
                'title':
                    f'{cls.user.get_full_name()} профайл пользователя',
                'author': cls.user,
            }),
            (cls.post_detail_url, {
                'title':
                    f'Пост {cls.post.text[:FIRST_SYMBOL_POST]}',
                'is_author': cls.post.author == cls.user,
            }),
            (cls.post_edit_url, {
                'is_edit': True,
                'post_id': cls.post.id,
            }),
        )

        cls.data_correct_form = (
            (cls.post_create_url, {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
                'image': forms.fields.ImageField,
            }),
            (cls.post_edit_url, {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
                'image': forms.fields.ImageField,
            }),
        )

        cls.group_other = GroupFactory.create()
        cls.post_other = PostFactory.create(
            author=cls.user, group=cls.group_other)
        cls.data_additional_test = (
            cls.index_url, cls.group_post_url, cls.profile_url,)

        cls.data_paginator_page = (
            (cls.index_url, '', LIMIT_POSTS),
            (cls.index_url, '?page=2', cls.PAGINATOR_TWO_PAGE_COUNT + 1),
            (cls.group_post_url, '', LIMIT_POSTS),
            (cls.group_post_url, '?page=2', cls.PAGINATOR_TWO_PAGE_COUNT),
        )

        cls.data_image_page = (
            cls.index_url,
            cls.profile_url,
            cls.group_post_url,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_show_correct_template_and_context(self):
        for url, values in self.data_correct_page:
            with self.subTest(adress=url.address):
                response = self.authorized_client.get(
                    reverse(url.address, args=url.args)
                )
                self.assertTemplateUsed(response, url.template)
                for value, expected in values.items():
                    self.assertEqual(response.context.get(value), expected)

    def test_form_page_show_correct_context(self):
        for url, values in self.data_correct_form:
            for value, expected in values.items():
                with self.subTest(adress=url.address, value=value):
                    response = self.authorized_client.get(reverse(
                        url.address, args=url.args))
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_paginator_num_records(self):
        for url, page2, expected in self.data_paginator_page:
            with self.subTest(address=url.address + page2):
                response = self.authorized_client.get(reverse(
                    url.address, args=url.args) + page2)
                self.assertEqual(len(response.context['page_obj']), expected)

    def test_additional_verification_and_image_when_creating_post(self):
        for url in self.data_additional_test:
            with self.subTest(adress=url.address):
                response = self.authorized_client.get(
                    reverse(url.address, args=url.args)
                )
                posts = [post.id for post in response.context['page_obj']]
                self.assertIn(self.post.id, posts)
                images = [post.image for post in response.context['page_obj']]
                self.assertIn(self.post.image, images)

        response = self.authorized_client.get(
            reverse(self.group_post_url.address,
                    args=self.group_post_url.args)
        )
        posts = [post.id for post in response.context['page_obj']]
        self.assertNotIn(self.post_other.id, posts)

        response = self.authorized_client.get(
            reverse(self.post_detail_url.address,
                    args=self.post_detail_url.args)
        )
        post = response.context.get('post')
        self.assertEqual(post.image, self.post.image)

    def test_cache(self):
        post_test = PostFactory.create(author=self.user)
        post_test_id = post_test.id
        response = self.authorized_client.get(
            reverse(self.index_url.address)
        )
        posts = [post.id for post in response.context['page_obj']]
        self.assertIn(post_test_id, posts)

        post_test.delete()
        response_cache = self.authorized_client.get(
            reverse(self.index_url.address)
        )
        self.assertEqual(response.content, response_cache.content)

        cache.clear()
        response_cache_clear = self.authorized_client.get(
            reverse(self.index_url.address)
        )
        posts = [post.id for post in response_cache_clear.context['page_obj']]
        self.assertNotIn(post_test_id, posts)

    def test_follow(self):
        author_follow = UserFactory.create()
        author_unfollow = UserFactory.create()
        response = self.authorized_client.get(
            reverse(self.profile_follow_url, args=(author_follow, ))
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(self.user.follower.filter(
            author=author_follow).exists())

        post_follow = PostFactory.create(author=author_follow)
        cache.clear()
        response = self.authorized_client.get(
            reverse(self.follow_index_url[0]))
        posts = [post.id for post in response.context['page_obj']]
        self.assertIn(post_follow.id, posts)

        post_unfollow = PostFactory.create(author=author_unfollow)
        cache.clear()
        response = self.authorized_client.get(
            reverse(self.follow_index_url[0]))
        posts = [post.id for post in response.context['page_obj']]
        self.assertNotIn(post_unfollow.id, posts)

        response = self.authorized_client.get(
            reverse(self.profile_unfollow_url, args=(author_follow,))
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(self.user.follower.filter(
            author=author_follow).exists())
