from typing import Any, Sequence

import factory
from django.contrib.auth import get_user_model

from .models import Article, Comment

User = get_user_model()


class ArticleFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: f'article-title-{n}')
    text = factory.Sequence(lambda n: f'article-text-{n}')

    class Meta:
        model = Article


class CommentFactory(factory.DjangoModelFactory):
    article = factory.SubFactory('tests.factories.ArticleFactory')
    text = factory.Sequence(lambda n: f'comment-text-{n}')

    class Meta:
        model = Comment


class UserFactory(factory.DjangoModelFactory):
    username = factory.Sequence(lambda n: 'username-{n}')
    email = factory.Faker('email')

    class Meta:
        model = User

    @factory.post_generation
    def password(self, _create: bool, extracted: Sequence[Any], **_kwargs):
        password = (
            extracted
            if extracted
            else factory.Faker(
                'password',
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).generate(extra_kwargs={})
        )
        self.set_password(password)
