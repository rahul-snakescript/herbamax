from __future__ import unicode_literals

from django.db import models
from redactor.fields import RedactorField
from mainapp.functions import unique_slugify, upload_blog_images_to


class Category(models.Model):
    name = models.CharField(max_length=128, unique=False)
    slug = models.SlugField(unique=False)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        unique_slugify(self, self.name)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Categories'


class Post(models.Model):
    title = models.CharField(max_length=200, blank=False)
    featured_image = models.ImageField(upload_to=upload_blog_images_to, blank=True, null=True)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ManyToManyField(Category)
    body = RedactorField(verbose_name=u'Body', allow_image_upload=True, allow_file_upload=False,  blank=True)

    created_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        unique_slugify(self, self.title)
        super(Post, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_date']
