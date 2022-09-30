from django.views.generic import ListView, DetailView
from django.db.models import Q
from models import Post


class BlogMainPageView(ListView):
    template_name = 'mainapp/blog/blog_main_page.html'
    model = Post
    paginate_by = 10

    def get_queryset(self):
        queryset = super(BlogMainPageView, self).get_queryset()
        if self.request.GET.get('cat'):
            queryset = queryset.filter(category__slug=self.request.GET.get('cat'))
        if self.request.GET.get('q'):
            q = self.request.GET.get('q')
            queryset = queryset.filter(Q(title__icontains=q) | Q(body__icontains=q))
        return queryset


class BlogPostView(DetailView):
    template_name = 'mainapp/blog/blog_post.html'
    model = Post
