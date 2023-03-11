from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from api.models import Category, Genre, Title
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


