from django.contrib.auth import get_user_model
from factory import Faker as boy_Faker
from factory.django import DjangoModelFactory
from posts.models import Post, Group


User = get_user_model()


class GroupFactory(DjangoModelFactory):
    title = boy_Faker(provider='text', max_nb_chars=20)
    slug = boy_Faker('slug')
    description = boy_Faker('sentence')

    class Meta:
        model = Group


class PostFactory(DjangoModelFactory):
    text = boy_Faker('text')

    class Meta:
        model = Post


class UserFactory(DjangoModelFactory):
    username = boy_Faker('user_name')
    first_name = boy_Faker('first_name')
    last_name = boy_Faker('last_name')

    class Meta:
        model = User
