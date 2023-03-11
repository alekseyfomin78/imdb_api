from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from .validators import validate_year


User = get_user_model()


class Category(models.Model):

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.slug


class Genre(models.Model):

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.slug


class Title(models.Model):

    name = models.CharField(max_length=200)
    year = models.IntegerField(validators=[validate_year])
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL, related_name="titles")
    genre = models.ManyToManyField(Genre, blank=True, null=True, related_name='titles')

    def __str__(self):
        return self.name


class Review(models.Model):

    text = models.TextField()
    title_id = models.ForeignKey(Title, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        error_messages={'validators': 'The score must be in the range of 1 to 10.'}
    )

    class Meta:
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

    text = models.TextField()
    review_id = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    pub_date = models.DateTimeField("date published", auto_now_add=True)

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text
