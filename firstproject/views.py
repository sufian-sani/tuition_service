from django.shortcuts import render, HttpResponse
from django.views.generic import TemplateView

def home(request):
    name = ['fahad', 'hossain','fahmida','farhana']
    content={'name': name}
    return render(request, 'home.html', content)

class HomeView(TemplateView):
    template_name = 'home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mes']="Welcome to our website"
        context['mes2']="Welcome to our website Again"
        return context
