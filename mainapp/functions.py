import re
import uuid
from decimal import Decimal, ROUND_HALF_UP
from django.template.defaultfilters import slugify


def unique_slugify(instance, value, slug_field_name='slug', queryset=None,
                   slug_separator='-'):
    """
    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '%s%s' % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len-len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)


def _slug_strip(value, separator='-'):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """
    separator = separator or ''
    if separator == '-' or not separator:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(separator)
    # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub('%s+' % re_sep, separator, value)
    # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != '-':
            re_sep = re.escape(separator)
        value = re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)
    return value


def get_tax_for_province(province, total):
    percent = 0.0
    dollars = Decimal(0.0)

    if province in ['ON', 'MB']:
        percent = 13.0
    elif province in ['AB', 'NT', 'NU', 'YT']:
        percent = 5.0
    elif province == 'SK':
        percent = 10.0
    elif province == 'BC':
        percent = 12.0
    elif province in ['NB', 'NL', 'NS', 'PE']:
        percent = 15.0
    elif province == 'QC':
        percent = 14.975
    dollars = total * Decimal(percent) / Decimal(100)
    dollars = dollars.quantize(Decimal('.01'), ROUND_HALF_UP)
    return percent, dollars


# UPLOAD TO


def upload_product_images_to(instance, filename):
    return upload_to(filename, 'product')


def upload_blog_images_to(instance, filename):
    return upload_to(filename, 'blog')


def upload_to(filename, folder):
    ext = filename.split('.')[-1]
    uuid_hash = str(uuid.uuid4())[:8]
    filename = '{0}.{1}'.format(uuid_hash, ext)
    return '%s/%s' % (folder, filename)
