from typing import Any, Sequence

import factory
from django.contrib.auth import get_user_model

from .models import Article, Comment

User = get_user_model()


class ArticleFactory(factory.django.DjangoModelFactory):
    title = factory.Sequence(lambda n: f'article-title-{n}')
    text = factory.Sequence(lambda n: f'article-text-{n}')

    class Meta:
        model = Article


class CommentFactory(factory.django.DjangoModelFactory):
    article = factory.SubFactory('tests.factories.ArticleFactory')
    text = factory.Sequence(lambda n: f'comment-text-{n}')

    class Meta:
        model = Comment


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: 'username-{n}')
    password = factory.Faker(
        'password',
        length=10,
        special_chars=True,
        digits=True,
        upper_case=True,
        lower_case=True,
    )
    email = factory.Faker('email')

    class Meta:
        model = User
