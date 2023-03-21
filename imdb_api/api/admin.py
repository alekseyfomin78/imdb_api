from django.contrib import admin
from users.models import User
from .models import Category, Genre, Title, Review, Comment


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email', 'role', 'is_superuser', 'is_staff',
                    'is_active')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')


class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')


class ReviewInline(admin.StackedInline):
    model = Review
    readonly_fields = ('author', 'score',)  # поля, в которые admin не может внести изменения
    extra = 1  # вывод только 1 дополнительной формы для создания отзыва (по умолчанию их 3)


class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'year', 'category', 'get_genres')
    search_fields = ('name',)
    list_filter = ('year', 'category', 'genre')
    inlines = [ReviewInline]  # дополнительно выводятся отзывы к произведению
    save_on_top = True  # добавление панели сохранения в верхнюю часть страницы

    # вывод жанров к произведению, поскольку связь M2M, то используем доп. функцию
    def get_genres(self, obj):
        return ", ".join([str(g) for g in obj.genre.all()])


class CommentInline(admin.StackedInline):
    model = Comment
    readonly_fields = ('author',)
    extra = 1


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'title_id', 'author', 'score', 'pub_date')
    search_fields = ('text', 'author__username', 'title_id__name')
    list_filter = ('pub_date',)
    readonly_fields = ('author', 'score')
    inlines = [CommentInline]  # дополнительно выводятся комментарии к отзыву
    save_on_top = True


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'review_id', 'author', 'pub_date')
    search_fields = ('text', 'review_id__text', 'author__username',)
    list_filter = ('pub_date',)
    readonly_fields = ('author',)


admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
