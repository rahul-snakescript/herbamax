from __future__ import unicode_literals
import json
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.mail import send_mail
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.conf import settings
from django.core.urlresolvers import reverse
from redactor.fields import RedactorField
from solo.models import SingletonModel
from mptt.models import MPTTModel, TreeForeignKey
from mainapp.functions import upload_product_images_to
from .functions import unique_slugify


'''
CUSTOM USER
'''


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """Create and save an EmailUser with the given email and password.
        :param str email: user email
        :param str password: user password
        :param bool is_staff: whether user staff or not
        :param bool is_superuser: whether user admin or not
        :return custom_user.models.EmailUser user: user
        :raise ValueError: email is not set
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        is_active = extra_fields.pop("is_active", True)
        user = self.model(email=email, is_staff=is_staff, is_active=is_active,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save an EmailUser with the given email and password.
        :param str email: user email
        :param str password: user password
        :return custom_user.models.EmailUser user: regular user
        """
        is_staff = extra_fields.pop("is_staff", False)
        return self._create_user(email, password, is_staff, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save an EmailUser with the given email and password.
        :param str email: user email
        :param str password: user password
        :return custom_user.models.EmailUser user: admin user
        """
        return self._create_user(email, password, True, True,
                                 **extra_fields)


class AbstractCustomUser(AbstractBaseUser, PermissionsMixin):
    """Abstract User with the same behaviour as Django's default User.
    AbstractEmailUser does not have username field. Uses email as the
    USERNAME_FIELD for authentication.
    Use this if you need to extend EmailUser.
    Inherits from both the AbstractBaseUser and PermissionMixin.
    The following attributes are inherited from the superclasses:
        * password
        * last_login
        * is_superuser
    """

    email = models.EmailField(_('email address'), max_length=255,
                              unique=True, db_index=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=False)
    last_name = models.CharField(_('last name'), max_length=30, blank=False)
    is_staff = models.BooleanField(
        _('staff status'), default=False, help_text=_(
            'Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True, help_text=_(
        'Designates whether this user should be treated as '
        'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this User."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class HmAdditionalUserFieldsMixin(models.Model):
    COUNTRIES_CHOICES = (
        ('CA', 'Canada'),
    )

    PROVINCES_CHOICES = (
        ('ON', 'Ontario'),
        ('AB', 'Alberta'),
        ('BC', 'British Columbia'),
        ('MB', 'Manitoba'),
        ('NB', 'New Brunswick'),
        ('NL', 'Newfoundland and Labrador'),
        ('NT', 'Northwest Territories'),
        ('NS', 'Nova Scotia'),
        ('NU', 'Nunavut'),
        ('PE', 'Prince Edward Island'),
        ('QC', 'Quebec'),
        ('SK', 'Saskatchewan'),
        ('YT', 'Yukon'),
    )

    b_first_name = models.CharField(max_length=60, blank=True, null=True, verbose_name='Billing First Name')
    b_last_name = models.CharField(max_length=60, blank=True, null=True, verbose_name='Billing Last Name')
    b_phone = models.CharField(max_length=60, blank=True, null=True, verbose_name='Billing Phone')
    # b_company = models.CharField(max_length=60, blank=True, null=True, verbose_name='Billing Company Name')
    b_country = models.CharField(max_length=60, blank=False, null=False, verbose_name='Billing Country',
                                 choices=COUNTRIES_CHOICES, default='CA')
    b_address = models.CharField(max_length=100, blank=True, null=True, verbose_name='Billing Address')
    b_city = models.CharField(max_length=60, blank=True, null=True, verbose_name='Billing City')
    b_state = models.CharField(max_length=60, blank=False, null=False, verbose_name='Billing State/Province',
                               choices=PROVINCES_CHOICES, default='ON')
    b_zip = models.CharField(max_length=60, blank=True, null=True, verbose_name='Billing Postcode/ZIP')

    s_first_name = models.CharField(max_length=60, blank=True, null=True, verbose_name='Shipping First Name')
    s_last_name = models.CharField(max_length=60, blank=True, null=True, verbose_name='Shipping Last Name')
    s_phone = models.CharField(max_length=60, blank=True, null=True, verbose_name='Shipping Phone')
    # s_company = models.CharField(max_length=60, blank=True, null=True, verbose_name='Shipping Company Name')
    s_country = models.CharField(max_length=60, blank=False, null=False, verbose_name='Shipping Country',
                                 choices=COUNTRIES_CHOICES, default='CA')
    s_address = models.CharField(max_length=100, blank=True, null=True, verbose_name='Shipping Address')
    s_city = models.CharField(max_length=60, blank=True, null=True, verbose_name='Shipping City')
    s_state = models.CharField(max_length=60, blank=False, null=False, verbose_name='Shipping State/Province',
                               choices=PROVINCES_CHOICES, default='ON')
    s_zip = models.CharField(max_length=60, blank=True, null=True, verbose_name='Shipping Postcode/ZIP')

    class Meta:
        abstract = True


class HmUser(AbstractCustomUser, HmAdditionalUserFieldsMixin):

    class Meta(AbstractCustomUser.Meta):
        swappable = 'AUTH_USER_MODEL'

'''
MODELS
'''


class Review(models.Model):
    text = models.TextField(blank=False)
    author = models.CharField(max_length=100, blank=False)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Ingredient(models.Model):
    name = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=100, blank=False)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class CouponCode(models.Model):
    code = models.CharField(max_length=50, blank=False, null=False)
    discount = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False, default=0.0)

    def __unicode__(self):
        return self.code


class Order(HmAdditionalUserFieldsMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False, default=0.0)
    total = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False, default=0.0)

    email = models.EmailField(max_length=255, unique=False)

    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False, default=0.0)
    tax_in_percents = models.FloatField(blank=False, null=False, default=0.0)
    tax_in_dollars = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False, default=0.0)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    coupon_code_discount = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False, default=0.0)

    note = models.TextField(blank=True, null=True, verbose_name='Order Notes')

    products = models.TextField(null=True, blank=True)
    response_order_id = models.CharField(null=True, blank=True, max_length=50)
    paid = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)

    def get_products_json(self):
        return json.loads(self.products)

    def __unicode__(self):
        return self.email

    class Meta:
        ordering = ('-created_date',)


class Page(models.Model):
    title = models.CharField(max_length=200, blank=False)
    url = models.CharField(max_length=200, blank=True, null=True, verbose_name='URL name')
    created_date = models.DateTimeField(auto_now_add=True)

    seo_title = models.CharField(max_length=100, blank=True, null=True)
    seo_description = models.CharField(max_length=160, blank=True, null=True)
    seo_keywords = models.CharField(max_length=255, blank=True, null=True)

    def get_absolute_url(self):
        try:
            return self.basicpage.get_absolute_url()
        except BasicPage.DoesNotExist:
            pass
        try:
            return self.product.get_absolute_url()
        except Product.DoesNotExist:
            pass
        return reverse(self.url)

    def __unicode__(self):
        try:
            return '(Basic Page) %s' % self.basicpage.__unicode__()
        except BasicPage.DoesNotExist:
            pass
        try:
            return '(Product Page) %s' % self.product.__unicode__()
        except Product.DoesNotExist:
            pass
        return self.title

    class Meta:
        ordering = ['title']


class BasicPage(Page):
    slug = models.SlugField(max_length=200, unique=True)
    body = RedactorField(verbose_name=u'Body', blank=True, allow_image_upload=True, allow_file_upload=True)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('page', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        unique_slugify(self, self.title)
        super(BasicPage, self).save(*args, **kwargs)

    get_absolute_url.short_description = 'URL'


class Product(Page):
    # title = models.CharField(max_length=200, blank=False)
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField(upload_to=upload_product_images_to, blank=False, null=False)
    npn = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False, default=0.0)
    discount = models.DecimalField(verbose_name=u'Discount %', max_digits=8, decimal_places=2, blank=False, null=False,
                                   default=0.0)
    short_description = RedactorField(verbose_name=u'Short Description', blank=True, allow_image_upload=True,
                                      allow_file_upload=False)
    full_description = RedactorField(verbose_name=u'Full Description', blank=True, allow_image_upload=True,
                                     allow_file_upload=False)
    reviews = GenericRelation(Review)
    ingredients = GenericRelation(Ingredient)
    # created_date = models.DateTimeField(default=timezone.now)

    def get_total(self):
        if self.discount:
            disc = float(self.price) * float(self.discount) / 100
            return round(float(self.price) - disc, 2)
        else:
            return self.price

    def get_absolute_url(self):
        return reverse('product', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        unique_slugify(self, self.title)
        super(Product, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title


class TopNavigationItem(MPTTModel):
    name = models.CharField(max_length=128, unique=False)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    page = models.ForeignKey(Page, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def get_link(self):
        if self.page:
            return self.page.get_absolute_url()
        else:
            return '#'

    class Meta:
        verbose_name = "Top Navigation Item"
        verbose_name_plural = "Top Navigation Items"
        unique_together = (("name", "parent",),)

    class MPTTMeta:
        order_insertion_by = ['name']


class SiteConfiguration(SingletonModel):
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, blank=False, null=False, default=0.0)
    banner_product = models.OneToOneField(Product, blank=True, null=True)
    email_list = models.TextField(blank=True, null=True, help_text='comma separated')

    def get_email_list(self):
        if self.email_list:
            return [x.strip() for x in self.email_list.split(',')]
        else:
            return []

    def __unicode__(self):
        return u"Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"
