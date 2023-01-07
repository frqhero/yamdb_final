from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User"""
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'bio',
            'role',
            'first_name',
            'last_name',)


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        user_exists = User.objects.filter(username=value).exists()
        if user_exists:
            raise serializers.ValidationError('username is already taken')
        return value

    def validate_email(self, value):
        user_exists = User.objects.filter(email=value).exists()
        if user_exists:
            raise serializers.ValidationError('email is already taken')
        return value


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code'
        )


class ForNotAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'bio',
            'role',
            'first_name',
            'last_name',)
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'name',
            'slug',
        )
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'name',
            'slug',
        )
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'genre',
            'category',
            'description'
        )
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug', queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(
        slug_field='slug', many=False, queryset=Category.objects.all())

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'genre',
            'category',
            'description'
        )
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        if self.context['view'].action == 'create':
            current_user = self.context['request'].user
            title_id = self.context['view'].kwargs['title_id']
            reviewed = Review.objects.filter(
                author=current_user, title__id=title_id).exists()
            if reviewed:
                raise serializers.ValidationError('an author allowed'
                                                  'to review once')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
        read_only_fields = ('author',)
