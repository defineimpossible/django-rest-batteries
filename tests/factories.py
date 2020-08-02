import factory

from .models import Article, Comment


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
