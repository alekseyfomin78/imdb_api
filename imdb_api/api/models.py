from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from .validators import validate_year


User = get_user_model()


class Category(models.Model):
    name = models.CharField('category name', max_length=200)
    slug = models.SlugField('category slug', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.slug


class Genre(models.Model):

    name = models.CharField('genre name', max_length=200)
    slug = models.SlugField('genre slug', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.slug


class Title(models.Model):

    name = models.CharField('name of title', max_length=200)
    year = models.IntegerField('year of creation', validators=[validate_year])
    category = models.ForeignKey(
        Category,
        verbose_name='category',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="titles"
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='genre',
        blank=True,
        null=True,
        related_name='titles'
    )

    class Meta:
        verbose_name = 'Title'
        verbose_name_plural = 'Titles'

    def __str__(self):
        return self.name


class Review(models.Model):

    text = models.TextField('review text')
    title = models.ForeignKey(
        Title,
        verbose_name='title',
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    author = models.ForeignKey(
        User,
        verbose_name='author',
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='score',
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        error_messages={'validators': 'The score must be in the range of 1 to 10.'},
        help_text='The score must be in the range of 1 to 10.'
    )
    pub_date = models.DateTimeField('date published', auto_now_add=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ["-pub_date"]
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_score_range",
                check=models.Q(score__range=(1, 10)),
            ),
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):

    text = models.TextField('comment text')
    review = models.ForeignKey(
        Review,
        verbose_name='review',
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        User,
        verbose_name='author',
        on_delete=models.CASCADE,
        related_name="comments"
    )
    pub_date = models.DateTimeField('date published', auto_now_add=True)

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text
