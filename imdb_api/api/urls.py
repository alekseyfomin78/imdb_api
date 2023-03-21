from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views


router = DefaultRouter()
router.register(r'categories', viewset=views.CategoryViewSet, basename='categories')
router.register(r'genres', viewset=views.GenreViewSet, basename='genres')

urlpatterns = [
    # categories, genres
    path('v1/', include(router.urls)),
    # titles
    path('v1/titles/', view=views.TitleListCreateView.as_view()),
    path('v1/titles/<int:title_id>/', view=views.TitleRetrieveUpdateDestroyView.as_view()),
    # reviews
    path('v1/titles/<int:title_id>/reviews/', view=views.ReviewListCreateView.as_view()),
    path('v1/titles/<int:title_id>/reviews/<int:review_id>/', view=views.ReviewRetrieveUpdateDestroyView.as_view()),
    # comments
    path('v1/titles/<int:title_id>/reviews/<int:review_id>/comments/', view=views.CommentListCreateView.as_view()),
    path(
        'v1/titles/<int:title_id>/reviews/<int:review_id>/comments/<int:comment_id>/',
        view=views.CommentRetrieveUpdateDestroyView.as_view()
    ),

    # jwt token
    path('v1/token/', view=TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/token/refresh/', view=TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/auth/email/', view=views.APISignup.as_view()),
    path('v1/auth/token/', view=views.APIJWTToken.as_view()),
]
