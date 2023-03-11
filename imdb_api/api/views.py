from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, filters, mixins
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from django.core.mail import EmailMessage
from users.models import User
from .confirmation_code import ConfirmationCodeGenerator
from .models import Category
from .permissions import IsNotAuth, IsAdminOrReadOnly
from .serializer import (
    UserSerializer,
    ConfirmationCodeSerializer,
    TokenSerializer,
    CategorySerializer,
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

