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


class ReviewReadSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='username')
    title = serializers.SlugRelatedField(queryset=Title.objects.all(), slug_field='name')

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        model = Review


class ReviewWriteSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField()

    class Meta:
        fields = ('id', 'text', 'score', 'pub_date')
        model = Review

    def validate_score(self, value):
        if not 0 < value <= 10:
            raise serializers.ValidationError('The score must be in the range of 1 to 10.')
        return value

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
                request.method == 'POST'
                and Review.objects.filter(title=title, author=author).exists()
        ):
            raise serializers.ValidationError('The review of this title already exists.')
        return data

