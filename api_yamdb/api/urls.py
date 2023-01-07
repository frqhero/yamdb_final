from django.urls import include, path
from api.views import (
    CategoryViewSet,
    GenreViewSet,
    SignUpAPIView,
    TitleViewSet,
    TokenAPIView,
    UsersViewSet,
    ReviewViewSet,
    CommentViewSet
)
from rest_framework.routers import DefaultRouter


v1_router = DefaultRouter()

v1_router.register('users', UsersViewSet)
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register(r'^titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                   basename='review')
v1_router.register(
    r'^titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment')

urlpatterns = [
    path('v1/auth/token/', TokenAPIView.as_view(), name='token'),
    path('v1/auth/signup/', SignUpAPIView.as_view(), name='signup'),
    path('v1/', include(v1_router.urls)),
]
