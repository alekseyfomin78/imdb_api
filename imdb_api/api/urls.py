from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views


# router = DefaultRouter()
# router.register(r'users', PostViewSet, basename='posts')
# router.register(r'posts/(?P<post_id>\d+)/comments', CommentViewSet, basename='comments')
# router.register(r'groups', GroupViewSet, basename='groups')
# router.register(r'follow', FollowViewSet, basename='follow')

urlpatterns = [
    # path('v1/', include(router.urls)),
    # jwt token
    # path('v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/auth/email/', view=views.APISignup.as_view()),
    path('v1/auth/token/', view=views.APIJWTToken.as_view()),
]
