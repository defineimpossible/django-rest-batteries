from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Article, Comment

User = get_user_model()


class CommentResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'id',
            'text',
        )


class ArticleResponseSerializer(serializers.ModelSerializer):
    comments = CommentResponseSerializer(many=True)

    class Meta:
        model = Article
        fields = (
            'id',
            'title',
            'text',
            'comments',
        )


class CommentRequestSerializer(serializers.ModelSerializer):
    article_id = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.filter(is_deleted=False), source='article'
    )

    class Meta:
        model = Comment
        fields = (
            'article_id',
            'text',
        )


class ArticleRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = (
            'title',
            'text',
        )


class ArticleDeleteSerializer(serializers.Serializer):
    with_comments = serializers.BooleanField(default=False)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
        )
