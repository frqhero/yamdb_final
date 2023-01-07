import random

from django.core.mail import EmailMessage
from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters1
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title, User

from .filters import TitleFilter
from .paginations import (PaginatorPageSize2, PaginatorPageSize3,
                          PaginatorPageSize4)
from .permissions import (AdminOnlyPermission, AdminOrReadOnlyPermission,
                          IsOwnerOrReadOnlyOrOfficial)
from .serializers import (CategorySerializer, CommentSerializer,
                          ForNotAdminSerializer, GenreSerializer,
                          ReviewSerializer, SignUpSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          TokenSerializer, UserSerializer)


class UsersViewSet(viewsets.ModelViewSet):
    """Класс для обработки запросов GET и PATCH модели User"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PaginatorPageSize4
    permission_classes = (AdminOnlyPermission,)

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='me'
    )
    def get_info_me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            if request.user.is_admin:
                serializer = UserSerializer(
                    user,
                    data=request.data,
                    partial=True)
            else:
                serializer = ForNotAdminSerializer(
                    user,
                    data=request.data,
                    partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['GET', 'PATCH', 'DELETE'],
        detail=False,
        url_path=r'(?P<username>\w+)'
    )
    def get_info_username(self, request, username):
        user = get_object_or_404(User, username=username)
        if request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = UserSerializer(
                user,
                data=request.data,
                partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenAPIView(APIView):
    """Получение JWT-токена в обмен на username и confirmation code."""

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if confirmation_code == user.confirmation_code:
            token = AccessToken.for_user(user)
            return Response({'token': str(token)},
                            status=status.HTTP_201_CREATED)
        return Response(
            {'confirmation_code': 'Неверный код!'},
            status=status.HTTP_400_BAD_REQUEST)


class SignUpAPIView(APIView):
    """Получить код подтверждения на электронную почту."""
    permission_classes = (permissions.AllowAny,)

    def send_email(self, data):
        email_message = EmailMessage(
            subject=data.get('email_subject'),
            body=data.get('email_text'),
            from_email='admin@example.com',
            to=[data.get('to E-mail')]
        )
        email_message.send()

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['username'] == 'me':
            return Response(
                serializer.data,
                status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        random.seed()
        code = str(random.randint(1000, 9999))
        user.confirmation_code = code
        user.save()
        email_text = (
            f'Здравствуйте, {user.username}. '
            f'\nКод подтверждения для доступа к API: {user.confirmation_code} '
            f'\nНе отвечайте на это письмо. Оно сгенерировано автоматически'
        )
        data = {
            'email_text': email_text,
            'to E-mail': user.email,
            'email_subject': 'Код подтверждения для доступа к API YaMDb!'
        }
        self.send_email(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PaginatorPageSize2
    permission_classes = (AdminOrReadOnlyPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PaginatorPageSize2
    permission_classes = (AdminOrReadOnlyPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Cast(Avg('reviews__score'),
                                            output_field=IntegerField()))
    permission_classes = (AdminOrReadOnlyPermission,)
    pagination_class = PaginatorPageSize2
    filter_backends = (filters1.DjangoFilterBackend,)
    filter_class = TitleFilter

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return TitleWriteSerializer
        else:
            return TitleReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnlyOrOfficial)
    pagination_class = PaginatorPageSize3

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = PaginatorPageSize4
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnlyOrOfficial)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
