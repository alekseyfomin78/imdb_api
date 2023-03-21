from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from api.models import Category, Genre, Title, Review, Comment
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='The user with this username already exists.'
        ), ],
        default=None,
    )

    email = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='The user with this email already exists.'
        ), ],
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'role')


class ConfirmationCodeSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token = token.access_token

        return token


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=250)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug',)
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug',)
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False, read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'category', 'genre', 'rating')


class TitleWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
        required=False
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
        required=False
    )

    class Meta:
        fields = '__all__'
        model = Title
