from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, filters, mixins, generics, views, viewsets
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from django.core.mail import EmailMessage
from users.models import User
from .confirmation_code import ConfirmationCodeGenerator
from .filters import TitleFilter
from .models import Category, Genre, Title
from .permissions import IsNotAuth, IsAdminOrReadOnly, IsAuthorOrModeratorOrAdminOrReadOnly
from django.db.models import Avg
from .serializer import (
    UserSerializer,
    ConfirmationCodeSerializer,
    TokenSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    ReviewReadSerializer,
    ReviewWriteSerializer,
    CommentSerializer,
)


confirmation_code_generator = ConfirmationCodeGenerator()


class APISignup(views.APIView):
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


class APIJWTToken(views.APIView):
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


class TitleListCreateView(generics.ListCreateAPIView):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleReadSerializer
        else:
            return TitleWriteSerializer

    # def perform_create(self, serializer):
    #     slug_genre = self.request.data.get('genre')
    #     if isinstance(slug_genre, str):
    #         slug_genre = self.request.data.getlist('genre')
    #     slug_category = self.request.data.get('category')
    #     genre = Genre.objects.filter(slug__in=slug_genre)
    #     category = get_object_or_404(Category, slug=slug_category)
    #     serializer.save(genre=genre, category=category)


class TitleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    lookup_url_kwarg = 'title_id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TitleWriteSerializer
        else:
            return TitleReadSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReviewReadSerializer
        else:
            return ReviewWriteSerializer


class ReviewRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,)
    lookup_field = 'title_id'

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.filter(id=self.kwargs.get('review_id'))

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ReviewWriteSerializer
        else:
            return ReviewReadSerializer


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination
    lookup_field = 'title_id'

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        review = title.reviews.get(id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        review = title.reviews.get(id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,)
    lookup_field = 'review_id'

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        review = title.reviews.get(id=self.kwargs.get('review_id'))
        return review.comments.filter(id=self.kwargs.get('comment_id'))
