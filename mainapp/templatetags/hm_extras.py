from django import template
from mainapp.models import TopNavigationItem
from blog.models import Post, Category

register = template.Library()


@register.inclusion_tag('mainapp/partials/nav_top.html', takes_context=True)
def get_top_nav(context):
    items = TopNavigationItem.objects.all()
    req = context['request']
    return {'path': req.path, 'items': items}


@register.inclusion_tag('mainapp/partials/blog_sidebar.html', takes_context=True)
def get_blog_sidebar(context):
    cats = Category.objects.all()
    latest_posts = Post.objects.all()[:5]
    request = context['request']
    return {'request': request, 'cats': cats, 'latest_posts': latest_posts}


@register.inclusion_tag('mainapp/partials/product_box.html')
def get_product_box(pr):
    return {'pr': pr}


@register.filter(name='addclass')
def addclass(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter(name='addclname')
def addclname(field, args):
    arg_list = [arg.strip() for arg in args.split(',')]
    return field.as_widget(attrs={"class": arg_list[0], "name": arg_list[1]})


@register.filter('fieldtype')
def fieldtype(ob):
    return ob.field.widget.__class__.__name__
