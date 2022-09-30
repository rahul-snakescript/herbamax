from django.contrib import admin
from models import Post, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    exclude = ('slug',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    exclude = ('slug',)
