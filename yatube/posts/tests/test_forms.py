import shutil
import tempfile
from http import HTTPStatus
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from posts.models import Post, Comment
from posts.tests.factorys import UserFactory, PostFactory

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


def post_response(client, address, data):
    return client.post(
        address,
        data=data,
        follow=True
    )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create()

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image_file_name = 'test_image.gif'
        uploaded = SimpleUploadedFile(
            name=cls.image_file_name,
            content=small_gif,
            content_type='image/gif'
        )
        cls.text_string_post = 'Текст из формы'
        cls.form_data_create_post = {
            'text': cls.text_string_post,
            'author': cls.user,
            'image': uploaded,
        }
        cls.post_query_data_post = {
            'text': cls.text_string_post,
            'author': cls.user,
            'image': 'posts/' + cls.image_file_name
        }
        cls.form_data_edit_post = {
            'text': cls.text_string_post + ' c изменениями', }
        cls.post_create_url = '/create/'
        cls.user_profile_url = f'/profile/{cls.user}/'

        cls.form_data_comment = {
            'text': 'test comments',
        }
        cls.comment_post = PostFactory.create(author=cls.user)
        cls.comment_add_url = f'/posts/{cls.comment_post.id}/comment/'
        cls.post_detail_url = f'/posts/{cls.comment_post.id}/'

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_and_edit_post(self):
        posts_count = Post.objects.count()
        response = post_response(
            self.authorized_client,
            self.post_create_url,
            self.form_data_create_post
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, self.user_profile_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertTrue(Post.objects.filter(
            **self.post_query_data_post).exists())
        post = Post.objects.get(**self.post_query_data_post)
        self.assertEqual(post.image, self.post_query_data_post['image'])
        post_edit_url = f'/posts/{post.id}/edit/'
        response = post_response(
            self.authorized_client,
            post_edit_url,
            self.form_data_edit_post
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_un_auth_user_cant_publish_post(self):
        posts_count = Post.objects.count()
        post_response(
            self.guest_client,
            self.post_create_url,
            self.form_data_create_post
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_create_comment(self):
        comment_count = Comment.objects.filter(
            post=self.comment_post.id).count()
        response = post_response(
            self.authorized_client,
            self.comment_add_url,
            self.form_data_comment
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, self.post_detail_url)
        self.assertEqual(
            Comment.objects.filter(post=self.comment_post.id).count(),
            comment_count + 1
        )

    def test_un_auth_user_cant_publish_comment(self):
        comment_count = Comment.objects.filter(id=self.comment_post.id).count()
        post_response(
            self.guest_client,
            self.comment_add_url,
            self.form_data_comment
        )
        self.assertEqual(
            Comment.objects.filter(id=self.comment_post.id).count(),
            comment_count
        )
