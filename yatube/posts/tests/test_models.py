from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import FIRST_SYMBOL_TITLE
from posts.tests.factorys import GroupFactory, PostFactory, UserFactory

User = get_user_model()


class PostModelTest(TestCase):
    def setUp(self):
        user = UserFactory.create()
        group = GroupFactory.create()
        self.post = PostFactory.create(
            author=user,
            text='Test_text_big_length ' * 10,
            group=group,
        )

    def test_models_have_correct_object_names(self):
        assert_job = {
            self.post: self.post.text[:FIRST_SYMBOL_TITLE],
            self.post.group: self.post.group.title,
        }
        for value, expected in assert_job.items():
            with self.subTest(value=value):
                self.assertEqual(str(value), expected)

    def test_verbose_name(self):
        fields_verbose = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'group': 'Группа',
            'image': 'Картинка',
        }
        for field, expected in fields_verbose.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name, expected)

    def test_help_text(self):
        fields_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for field, expected in fields_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected)
