import pytest
from django.contrib.auth import get_user_model
from rest_framework import routers
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_batteries.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    FullUpdateModelMixin,
    ListModelMixin,
    PartialUpdateModelMixin,
    RetrieveModelMixin,
)
from rest_batteries.viewsets import GenericViewSet, ModelViewSet

from . import factories as f
from .models import Article, Comment
from .serializers import (
    ArticleDeleteSerializer,
    ArticleRequestSerializer,
    ArticleResponseSerializer,
    CommentRequestSerializer,
    CommentResponseSerializer,
    UserSerializer,
)

User = get_user_model()


class ArticleViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    FullUpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Article.objects.all()
    action_permission_classes = {
        'list': (AllowAny,),
        'retrieve': AllowAny,
        'create': IsAuthenticated,
        'update': IsAuthenticated,
        'destroy': IsAuthenticated,
    }
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


class UserViewSet(PartialUpdateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    request_action_serializer_classes = {
        'update': UserSerializer,
    }
    response_action_serializer_classes = {
        'update': UserSerializer,
    }


router = routers.SimpleRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = router.urls


@pytest.fixture(autouse=True)
def root_urlconf(settings):
    settings.ROOT_URLCONF = __name__


class TestArticleViewSet:
    def test_create_article(self, test_user_api_client):
        title = 'test-article-title'
        text = 'test-article-text'
        response = test_user_api_client.post('/articles/', {'title': title, 'text': text})
        assert response.status_code == 201
        assert response.data['title'] == title
        assert response.data['text'] == text

    def test_create_article__when_not_authenticated(self, api_client):
        title = 'test-article-title'
        text = 'test-article-text'
        response = api_client.post('/articles/', {'title': title, 'text': text})
        assert response.status_code == 403

    def test_retrieve_article(self, api_client):
        article_1 = f.ArticleFactory.create()

        response = api_client.get(f'/articles/{article_1.id}/')
        assert response.status_code == 200
        assert response.data == ArticleResponseSerializer(article_1).data

    def test_list_articles(self, api_client):
        article_1 = f.ArticleFactory.create()

        response = api_client.get('/articles/')
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0] == ArticleResponseSerializer(article_1).data

    def test_update_article(self, test_user_api_client):
        article_1 = f.ArticleFactory.create()

        title = 'test-article-title'
        text = 'test-article-text'
        response = test_user_api_client.put(
            f'/articles/{article_1.id}/', {'title': title, 'text': text}
        )
        assert response.status_code == 200
        assert response.data['id'] == article_1.id
        assert response.data['title'] == title
        assert response.data['text'] == text

    def test_update_article__when_not_authenticated(self, api_client):
        article_1 = f.ArticleFactory.create()

        title = 'test-article-title'
        text = 'test-article-text'
        response = api_client.put(f'/articles/{article_1.id}/', {'title': title, 'text': text})
        assert response.status_code == 403

    def test_partial_update_article__method_not_allowed(self, test_user_api_client):
        article_1 = f.ArticleFactory.create()

        title = 'test-article-title'
        response = test_user_api_client.patch(f'/articles/{article_1.id}/', {'title': title})
        assert response.status_code == 405

    def test_destroy_article(self, test_user_api_client):
        article_1 = f.ArticleFactory.create()
        f.CommentFactory.create(article=article_1)
        f.CommentFactory.create(article=article_1)

        response = test_user_api_client.delete(f'/articles/{article_1.id}/')
        assert response.status_code == 204
        assert Article.objects.get(id=article_1.id).is_deleted is True
        assert Article.objects.get(id=article_1.id).comments.count() == 2

    def test_destroy_article__when_with_comments(self, test_user_api_client):
        article_1 = f.ArticleFactory.create()
        f.CommentFactory.create(article=article_1)
        f.CommentFactory.create(article=article_1)

        response = test_user_api_client.delete(
            f'/articles/{article_1.id}/', {'with_comments': True}
        )
        assert response.status_code == 204
        assert Article.objects.get(id=article_1.id).is_deleted is True
        assert Article.objects.get(id=article_1.id).comments.count() == 0

    def test_destroy_article__when_not_authenticated(self, api_client):
        article_1 = f.ArticleFactory.create()
        f.CommentFactory.create(article=article_1)
        f.CommentFactory.create(article=article_1)

        response = api_client.delete(f'/articles/{article_1.id}/')
        assert response.status_code == 403


class TestCommentViewSet:
    def test_create_comment(self, api_client):
        article_1 = f.ArticleFactory.create()

        text = 'test-comment-text'
        response = api_client.post('/comments/', {'article_id': article_1.id, 'text': text})
        assert response.status_code == 201
        assert response.data['text'] == text

    def test_retrieve_comment(self, api_client):
        comment_1 = f.CommentFactory.create()

        response = api_client.get(f'/comments/{comment_1.id}/')
        assert response.status_code == 200
        assert response.data == CommentResponseSerializer(comment_1).data

    def test_list_comments(self, api_client):
        comment_1 = f.CommentFactory.create()

        response = api_client.get('/comments/')
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


class TestUserViewSet:
    def test_partial_update_user(self, api_client):
        user_1 = f.UserFactory.create()

        username = 'test-username'
        response = api_client.patch(f'/users/{user_1.id}/', {'username': username})
        assert response.status_code == 200
        assert response.data['id'] == user_1.id
        assert response.data['username'] == username
