from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from . models import land

class landing(ListView):
    model = land
    template_name = 'alpha/landing.html'

class commu(ListView):
    model = land
    template_name = 'alpha/commu.html'

class codingtest(ListView):
    model = land
    template_name = 'alpha/codingtest.html'

class codingexam(ListView):
    model = land
    template_name = 'alpha/codingexam.html'