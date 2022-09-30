from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from solo.admin import SingletonModelAdmin
from mptt.admin import DraggableMPTTAdmin
from mainapp.models import Product, Review, Ingredient, SiteConfiguration, CouponCode, Order, TopNavigationItem, Page


class ReviewInline(GenericTabularInline):
    model = Review
    extra = 1
    ct_field_name = 'content_type'
    id_field_name = 'object_id'
    # suit_classes = 'suit-tab suit-tab-box3'


class IngredientInline(GenericTabularInline):
    model = Ingredient
    extra = 1
    ct_field_name = 'content_type'
    id_field_name = 'object_id'
    # suit_classes = 'suit-tab suit-tab-box3'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    exclude = 'slug', 'created_date', 'url'
    inlines = [ReviewInline, IngredientInline]


admin.site.register(SiteConfiguration, SingletonModelAdmin)
admin.site.register(CouponCode, admin.ModelAdmin)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'paid']


admin.site.register(
    TopNavigationItem,
    DraggableMPTTAdmin,
    list_display=(
        'tree_actions',
        'indented_title',
    ),
    list_display_links=(
        'indented_title',
    )
)

admin.site.register(Page, admin.ModelAdmin)
