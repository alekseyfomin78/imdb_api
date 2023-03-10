from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all()), ],
        error_messages={'required': 'The user with this username already exists.'},
        default=None,
    )

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all()), ],
        error_messages={'required': 'The user with this email already exists.'},
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
