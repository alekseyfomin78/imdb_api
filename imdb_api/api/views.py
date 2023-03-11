from django.shortcuts import get_list_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, filters, mixins
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from django.core.mail import EmailMessage
from users.models import User
from .confirmation_code import ConfirmationCodeGenerator
from .filters import TitleFilter
from .models import Category, Genre, Title
from .permissions import IsNotAuth, IsAdminOrReadOnly
from django.db.models import Avg
from .serializer import (
    UserSerializer,
    ConfirmationCodeSerializer,
    TokenSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleSerializer, TitleReadSerializer, TitleWriteSerializer,
)


confirmation_code_generator = ConfirmationCodeGenerator()


class APISignup(APIView):
    """
    API регистрации пользователя.
    Пользователь отправляет POST запрос с параметром email, если пользователя с таким email в БД не существует,
    то на этот email отправляется confirmation_code.
    """
    permission_classes = [IsNotAuth]  # доступно только для не аутентифицированных пользователей

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            # пользователь создается в БД, но имеет неактивный аккаунт
            user = User.objects.create(email=request.data.get('email'))
            user.is_active = False
            user.set_unusable_password()
            user.save()

            confirmation_code = confirmation_code_generator.make_token(user)
            mail_subject = 'Activate your account.'
            message = (f"Hello, your confirmation_code: "
                       f"{confirmation_code}")
            to_email = str(request.data.get('email'))

            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()

            return Response({'email': serializer.data['email']}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIJWTToken(APIView):
    """
    API подтверждения регистрации пользователя.
    Пользователь отправляет POST запрос с параметрами email и confirmation_code,
    если confirmation_code совпадает с тем, который был отправлен пользователю на email,
    то пользователь успешно регистрируется и в ответ получает token.
    """

    permission_classes = [IsNotAuth]

    def post(self, request):
        user = User.objects.get(email=request.data.get('email'))

        if confirmation_code_generator.check_token(user, request.data.get('confirmation_code')):
            user.is_active = True  # активация аккаунта пользователя
            user.save()
            data = {
                'token': str(ConfirmationCodeSerializer.get_token(user))
            }
            serializer = TokenSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):

    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    # serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer

    # def perform_create(self, serializer):
    #     slug_genre = self.request.data.get('genre')
    #     if isinstance(slug_genre, str):
    #         slug_genre = self.request.data.getlist('genre')
    #     slug_category = self.request.data.get('category')
    #     genre = Genre.objects.filter(slug__in=slug_genre)
    #     category = get_object_or_404(Category, slug=slug_category)
    #     serializer.save(genre=genre, category=category)
    #
    # def perform_update(self, serializer):
    #     slug_genre = self.request.data.get('genre')
    #     slug_category = self.request.data.get('category')
    #     if slug_genre and slug_category:
    #         genre = Genre.objects.filter(slug__in=slug_genre)
    #         category = get_object_or_404(Category, slug=slug_category)
    #         serializer.save(genre=genre, category=category)
    #     elif slug_genre:
    #         genre = get_list_or_404(Genre, slug__in=slug_genre)
    #         serializer.save(genre=genre)
    #     elif slug_category:
    #         category = get_object_or_404(Category, slug=slug_category)
    #         serializer.save(category=category)
    #     else:
    #         serializer.save()
