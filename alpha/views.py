from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from . models import land
import traceback


class landing(ListView):
    model = land
    template_name = 'alpha/landing.html'

class commu(ListView):
    model = land
    template_name = 'alpha/commu.html'

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