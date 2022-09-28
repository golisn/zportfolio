
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from .forms import CommentForm
from django.db.models import Q
import os
import re
from . models import Post_info, Post_qa, land, Post, Category, Tag, Comment
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.options import Options

# Create your views here.
from .models import Post, Category, Tag, Comment

class Codingtest(CreateView):
    model = land
    template_name = 'alpha/codingtest.html'
    fields = ['content']

class Landing(ListView):
    model = Post
    ordering = '-pk'
    template_name = 'alpha/landing.html'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(Landing, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['qa_object_list'] = Post_qa.objects.all()
        context['info_object_list'] = Post_info.objects.all()

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

#===========================commu_qa 페이지 리스트
class Commu_qa(ListView):
    model = Post_qa
    ordering = '-pk'
    template_name = 'alpha/commu_qa.html'
    paginate_by = 10
    context_object_name = 'qa_object_list'
    def get_context_data(self, **kwargs):
        context = super(Commu_qa, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        
        return context

class CommuCreate_qa(LoginRequiredMixin, UserPassesTestMixin, CreateView ):
    model = Post_qa
    template_name = 'alpha/commucreate.html'
    fields = ['title', 'content', 'head_image', 'file_upload', 'category']
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super(CommuCreate_qa, self).form_valid(form)

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


class CommuUpdate_qa(LoginRequiredMixin, UpdateView, PermissionDenied):    
    model = Post_qa
    fields = ['title', 'content', 'head_image', 'file_upload', 'category']
    template_name = 'alpha/commucreate.html'
    
    def get_context_data(self, **kwargs):
        context = super(CommuUpdate_qa, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommuUpdate_qa, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied
    def form_valid(self, form):
        response = super(CommuUpdate_qa, self).form_valid(form)
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


def new_comment_qa(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post_qa, pk=pk)

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

#===========================commu_info 페이지 리스트
class Commu_info(ListView):
    model = Post_info
    ordering = '-pk'
    template_name = 'alpha/commu_info.html'
    paginate_by = 10
    context_object_name = 'info_object_list'

    def get_context_data(self, **kwargs):
        context = super(Commu_info, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context

class CommuCreate_info(LoginRequiredMixin, UserPassesTestMixin, CreateView ):
    model = Post_info
    template_name = 'alpha/commucreate.html'
    fields = ['title', 'content', 'head_image', 'file_upload', 'category']
    
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super(CommuCreate_info, self).form_valid(form)

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


class CommuUpdate_info(LoginRequiredMixin, UpdateView, PermissionDenied):    
    model = Post_info
    fields = ['title', 'content', 'head_image', 'file_upload', 'category']
    template_name = 'alpha/commucreate.html'
    
    def get_context_data(self, **kwargs):
        context = super(CommuUpdate_info, self).get_context_data()
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            context['tags_str_default'] = '; '.join(tags_str_list)
        return context

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(CommuUpdate_info, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied
    def form_valid(self, form):
        response = super(CommuUpdate_info, self).form_valid(form)
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


def new_comment_info(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post_info, pk=pk)

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


# ================================================ coding test

import re

def coresult(request):
    cotest = request.POST.get('cote')

    with open('ipynb/test.ipynb', 'w')as f:
        f.write(f'''
{{
 "cells": [
  {{
   "cell_type": "code",
   "execution_count": null,
   "id": "69481cd9",
   "metadata": {{}},
   "outputs": [],
   "source": ["{cotest}"]
  }}
 ],
 "metadata": {{
  "kernelspec": {{
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  }},
  "language_info": {{
   "codemirror_mode": {{
    "name": "ipython",
    "version": 3
   }},
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.13"
  }},
  "toc": {{
   "base_numbering": 1,
   "nav_menu": {{}},
   "number_sections": true,
   "sideBar": true,
   "skip_h1_title": false,
   "title_cell": "Table of Contents",
   "title_sidebar": "Contents",
   "toc_cell": false,
   "toc_position": {{}},
   "toc_section_display": true,
   "toc_window_display": false
  }}
 }},
 "nbformat": 4,
 "nbformat_minor": 5
}}''')
    #============= 저장한 주피터노트북 파일 실행===============#
    
    options = Options()
    options.add_argument('headless')
    path = r"tool/chromedriver.exe"
    driver = webdriver.Chrome(path,options=options)
    
    driver.get("http://localhost:8888/notebooks/ipynb/test.ipynb")
    tdoit = driver.find_element(By.XPATH,'//*[@id="password_input"]')
    tdoit.send_keys('490c4f9f8d604aa643e7a017fa9c70191fb629080aa76625')
    tdoit.send_keys(Keys.ENTER)
    time.sleep(0.5)
    driver.find_element(By.XPATH,"//*[@id='celllink']").click()
    time.sleep(0.5)
    driver.find_element(By.XPATH, '//*[@id="run_cell"]/a/span[1]').click()
    time.sleep(0.5)
    driver.find_element(By.XPATH, '//*[@id="save-notbook"]/button').click()
    time.sleep(0.5)
    with open('ipynb/test.ipynb', 'r', encoding='utf-8') as f:
        test = f.read()

    dodo = re.findall(r'"outputs": .*? "source',test,re.DOTALL)

    result = []
    for i,_ in enumerate(dodo):
        result.append(dodo[i][:-6])
    driver.quit()
    return render(
        request, 'alpha/codingresult.html',
        {
            "result" : result[0],
        }
    )