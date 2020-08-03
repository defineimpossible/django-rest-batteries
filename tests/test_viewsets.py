import pytest
from rest_batteries.viewsets import ModelViewSet
from rest_framework import routers

from . import factories as f
from .models import Article, Comment
from .serializers import (
    ArticleDeleteSerializer,
    ArticleRequestSerializer,
    ArticleResponseSerializer,
    CommentRequestSerializer,
    CommentResponseSerializer,
)


class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    request_action_serializer_classes = {
        'create': ArticleRequestSerializer,
        'update': ArticleRequestSerializer,
        'destroy': ArticleDeleteSerializer,
    }
    response_action_serializer_classes = {
        'create': ArticleResponseSerializer,
        'retrieve': ArticleResponseSerializer,
        'list': ArticleResponseSerializer,
        'update': ArticleResponseSerializer,
    }

    def perform_destroy(self, instance, serializer=None):
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])

        if serializer is not None and serializer.validated_data.get('with_comments'):
            instance.comments.all().delete()


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    request_action_serializer_classes = {
        'create': CommentRequestSerializer,
        'update': CommentRequestSerializer,
        'partial_update': CommentRequestSerializer,
    }
    response_action_serializer_classes = {
        'create': CommentResponseSerializer,
        'retrieve': CommentResponseSerializer,
        'list': CommentResponseSerializer,
        'update': CommentResponseSerializer,
        'partial_update': CommentResponseSerializer,
    }


router = routers.SimpleRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = router.urls


@pytest.fixture(autouse=True)
def root_urlconf(settings):
    settings.ROOT_URLCONF = __name__


class TestArticleViewSet:
    def test_create_article(self, api_client):
        title = 'test-article-title'
        text = 'test-article-text'
        response = api_client.post(f'/articles/', {'title': title, 'text': text})
        assert response.status_code == 201
        assert response.data['title'] == title
        assert response.data['text'] == text

    def test_retrieve_article(self, api_client):
        article_1 = f.ArticleFactory.create()

        response = api_client.get(f'/articles/{article_1.id}/')
        assert response.status_code == 200
        assert response.data == ArticleResponseSerializer(article_1).data

    def test_list_articles(self, api_client):
        article_1 = f.ArticleFactory.create()

        response = api_client.get(f'/articles/')
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0] == ArticleResponseSerializer(article_1).data

    def test_update_article(self, api_client):
        article_1 = f.ArticleFactory.create()

        title = 'test-article-title'
        text = 'test-article-text'
        response = api_client.put(
            f'/articles/{article_1.id}/', {'title': title, 'text': text}
        )
        assert response.status_code == 200
        assert response.data['id'] == article_1.id
        assert response.data['title'] == title
        assert response.data['text'] == text

    def test_partial_update_article(self, api_client):
        article_1 = f.ArticleFactory.create()

        title = 'test-article-title'
        response = api_client.patch(f'/articles/{article_1.id}/', {'title': title})
        assert response.status_code == 200
        assert response.data['id'] == article_1.id
        assert response.data['title'] == title

    def test_destroy_article(self, api_client):
        article_1 = f.ArticleFactory.create()
        f.CommentFactory.create(article=article_1)
        f.CommentFactory.create(article=article_1)

        response = api_client.delete(f'/articles/{article_1.id}/')
        assert response.status_code == 204
        assert Article.objects.get(id=article_1.id).is_deleted is True
        assert Article.objects.get(id=article_1.id).comments.count() == 2

    def test_destroy_article__when_with_comments(self, api_client):
        article_1 = f.ArticleFactory.create()
        f.CommentFactory.create(article=article_1)
        f.CommentFactory.create(article=article_1)

        response = api_client.delete(
            f'/articles/{article_1.id}/', {'with_comments': True}
        )
        assert response.status_code == 204
        assert Article.objects.get(id=article_1.id).is_deleted is True
        assert Article.objects.get(id=article_1.id).comments.count() == 0


class TestCommentViewSet:
    def test_create_comment(self, api_client):
        article_1 = f.ArticleFactory.create()

        text = 'test-comment-text'
        response = api_client.post(
            f'/comments/', {'article_id': article_1.id, 'text': text}
        )
        assert response.status_code == 201
        assert response.data['text'] == text

    def test_retrieve_comment(self, api_client):
        comment_1 = f.CommentFactory.create()

        response = api_client.get(f'/comments/{comment_1.id}/')
        assert response.status_code == 200
        assert response.data == CommentResponseSerializer(comment_1).data

    def test_list_comments(self, api_client):
        comment_1 = f.CommentFactory.create()

        response = api_client.get(f'/comments/')
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0] == CommentResponseSerializer(comment_1).data

    def test_update_comment(self, api_client):
        article_1 = f.ArticleFactory.create()
        comment_1 = f.CommentFactory.create()

        text = 'test-comment-text'
        response = api_client.put(
            f'/comments/{comment_1.id}/', {'article_id': article_1.id, 'text': text}
        )
        assert response.status_code == 200
        assert response.data['id'] == comment_1.id
        assert response.data['text'] == text

    def test_partial_update_comment(self, api_client):
        comment_1 = f.CommentFactory.create()

        text = 'test-comment-title'
        response = api_client.patch(f'/comments/{comment_1.id}/', {'text': text})
        assert response.status_code == 200
        assert response.data['id'] == comment_1.id
        assert response.data['text'] == text

    def test_destroy_comment(self, api_client):
        comment_1 = f.CommentFactory.create()

        response = api_client.delete(f'/comments/{comment_1.id}/')
        assert response.status_code == 204
