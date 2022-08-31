from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from . models import land

class landing(ListView):
    model = land
    template_name = 'alpha/landing.html'