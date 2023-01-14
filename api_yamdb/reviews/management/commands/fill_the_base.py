import csv
import os

from django.core.management.base import BaseCommand

from ...models import Category, Comment, Genre, GenreTitle, Review, Title, User


def get_csv_folder_path():
    sought_module_path = os.path.dirname(__file__)
    for _ in range(3):
        sought_module_path = os.path.dirname(sought_module_path)
    return os.path.join(sought_module_path, 'staticc/data')


csvs_folderpath = get_csv_folder_path()


def csv_lines_list_to_dicts_list(csv_list):
    res = []
    columns = csv_list[0]
    for index in range(1, len(csv_list)):
        res.append(dict(zip(columns, csv_list[index])))
    return res


def get_dicts_list(filename):
    csv_filepath = os.path.join(csvs_folderpath, filename)
    with open(csv_filepath) as file:
        csv_list = list(csv.reader(file))
        return csv_lines_list_to_dicts_list(csv_list)


class Command(BaseCommand):
    def handle(self, *args, **options):
        # users
        dicts_list = get_dicts_list('users.csv')
        [User.objects.get_or_create(**x)
         for x in dicts_list]

        # category
        dicts_list = get_dicts_list('category.csv')
        Category.objects.all().delete()
        [Category.objects.get_or_create(**x)
         for x in dicts_list]

        # titles
        dicts_list = get_dicts_list('titles.csv')

        Title.objects.all().delete()

        for each in dicts_list:
            category = Category.objects.get(id=each['category'])
            each['category'] = category
            Title.objects.get_or_create(**each)

        # genre
        dicts_list = get_dicts_list('genre.csv')

        Genre.objects.all().delete()

        [Genre.objects.get_or_create(**x)
         for x in dicts_list]

        # genre_title
        dicts_list = get_dicts_list('genre_title.csv')

        GenreTitle.objects.all().delete()

        for each in dicts_list:
            title_id = each.pop('title_id')
            genre_id = each.pop('genre_id')
            each['title'] = Title.objects.get(id=title_id)
            each['genre'] = Genre.objects.get(id=genre_id)
            GenreTitle.objects.get_or_create(**each)

        # review
        dicts_list = get_dicts_list('review.csv')

        Review.objects.all().delete()

        for each in dicts_list:
            title_id = each.pop('title_id')
            each['title'] = Title.objects.get(id=title_id)
            each['author'] = User.objects.get(id=each['author'])

            Review.objects.get_or_create(**each)

        # comments
        dicts_list = get_dicts_list('comments.csv')

        Comment.objects.all().delete()

        for each in dicts_list:
            review_id = each.pop('review_id')
            each['review'] = Review.objects.get(id=review_id)
            each['author'] = User.objects.get(id=each['author'])

            Comment.objects.get_or_create(**each)
