from django.contrib import admin

from .models import User, Title, Genre, Category, GenreTitle, Review, Comment


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'role',
        'bio',
        'first_name',
        'last_name',
    )
    search_fields = ('username', 'role',)
    list_filter = ('username',)
    empty_value_display = '-пусто-'


class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category'
    )


class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug'
    )


class GenreTitleAdmin(admin.ModelAdmin):
    list_display = (
        'genre',
        'title'
    )


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'text_preview',
        'author',
        'title'
    )


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text_preview',
        'author',
        'review'
    )


admin.site.register(User, UserAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Category)
admin.site.register(GenreTitle, GenreTitleAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
