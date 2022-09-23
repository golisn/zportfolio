from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from .forms import CommentForm
from django.db.models import Q

from . models import land, Post, Category, Tag, Comment
import traceback

# Create your views here.
from .models import Post, Category, Tag, Comment

# class landing(ListView):
#     model = land
#     template_name = 'alpha/landing.html'

class codingexam(ListView):
    model = land
    template_name = 'alpha/codingexam.html'

class result(ListView):
    model = land
    template_name = 'alpha/result.html'

    def get_a_b(self, **kwargs):
        cotx = self.request.POST['content']
        return cotx

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["content"] = self.get_a_b()
        return context
    # def form_valid(self, form):
    #     response = super(codingtest, self).form_valid(form)
    #     return response
        

    # def get_pytest(self, **kwargs):
    #     testen = self.request.POST.get('content',None)
    #     try:
    #         return testen
    #     except Exception:
    #         err = traceback.format_exc()
    #         return err

    # def get_context_data(self, **kwargs):
    #     context = super(result, self).get_context_data()
    #     context['pytest'] = self.get_pytest()
    #     return context
class codingtest(CreateView):
    model = land
    template_name = 'alpha/codingtest.html'
    fields = ['content']

    def form_valid(self, form):
        return super().form_valid(form)

    # def get_a_b(self, **kwargs):
    #     cotx = self.request.GET.get('content')
    #     return cotx

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["content"] = self.get_a_b()
    #     return context

#==================landing페이지 및 디테일 페이지


class Landing(ListView):
    model = Post
    ordering = '-pk'
    template_name = 'alpha/landing.html'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(Landing, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context


class CommuDetail(DetailView):
    model = Post
    template_name = 'alpha/commu_detail.html'

    def get_context_data(self, **kwargs):
        context = super(CommuDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['comment_form'] = CommentForm
        return context
    

def category_page(request, slug):
    if slug =='no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(
        request,
        'alpha/landing.html',
        {
            'object_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category': category,
        }
    )


def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    return render(
        request,
        'alpha/landing.html',
        {
            'object_list': post_list,
            'tag' : tag,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
        }
    )


class CommuCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView ):
    model = Post
    template_name = 'alpha/commucreate.html'
    fields = ['title', 'content', 'head_image', 'file_upload', 'category']
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super(CommuCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')

            if tags_str:
                tags_str = tags_str.strip()
                tags_str = tags_str.replace(',',';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)
            
            return response

        else:
            return redirect('/')


class CommuUpdate(LoginRequiredMixin, UpdateView, PermissionDenied):    
    model = Post
    fields = ['title', 'content', 'head_image', 'file_upload', 'category']
    template_name = 'alpha/commucreate.html'
    
    def get_context_data(self, **kwargs):
        context = super(CommuUpdate, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommuUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied
    def form_valid(self, form):
        response = super(CommuUpdate, self).form_valid(form)
        self.object.tags.clear()

        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()
            tags_str = tags_str.replace(',',';')
            tags_list = tags_str.split(';')

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)
                    tag.save()
                self.object.tags.add(tag)
        
        return response


def new_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)

        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url())
            else:
                return redirect(post.get_absolute_url())
        else:
            raise PermissionDenied


class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post
    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied


class PostSearch(Landing):
    paginate_by = None

    def get_queryset(self):
        q = self.kwargs['q']
        post_list = Post.objects.filter(
            Q(title__contains=q) | Q(tags__name__contains=q)
        ).distinct()
        return post_list
    
    def get_context_data(self, **kwargs):
        context = super(PostSearch, self).get_context_data()
        q = self.kwargs['q']
        context["search_info"] = f'Search: {q} ({self.get_queryset().count()})'

        return context




#===========================commu 페이지 리스트
class Commu(ListView):
    model = Post
    ordering = '-pk'
    template_name = 'alpha/commu.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(Commu, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context