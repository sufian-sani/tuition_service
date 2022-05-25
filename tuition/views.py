from django.shortcuts import render, HttpResponse, redirect
from .models import *
from .forms import *

from django.views import View
from django.views.generic import FormView, CreateView, ListView, DetailView, UpdateView, DeleteView

from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .templatetags import tag

from notifications.signals import notify
from session.models import *
# Create your views here.

app_name = 'tuition'

def search(request):
    query=request.POST.get('search','')
    if query:
        queryset=(Q(title__icontains=query)) | (Q(details__icontains=query)) | (Q(medium__icontains=query)) | (Q(category__icontains=query)) | (Q(subject__name__icontains=query)) | (Q(class_in__name__icontains=query))
        results = Post.objects.filter(queryset).distinct()
    else:
        results=[]
    context={
        'results':results
    }
    return render(request, 'tuition/search.html', context)

def filter(request):
    if request.method == 'POST':
        subject=request.POST['subject']
        class_in=request.POST['class_in']
        salary_from=request.POST['salary_from']
        salary_to=request.POST['salary_to']
        available=request.POST['available']
        if subject or class_in:
            queryset=(Q(subject__name__icontains=subject)) & (Q(class_in__name__icontains=class_in))
            results = Post.objects.filter(queryset).distinct()
            if available:
                results=results.filter(available=True)
            if salary_from:
                results=results.filter(salary__gte=salary_from)
            if salary_to:
                results=results.filter(salary__lte=salary_to)
        else:
            results=[]

        context={
            'results':results
        }
        return render(request, 'tuition/search.html', context)

class ContactView(FormView):
    form_class = ContactForm
    template_name = 'contact.html'
    # success_url = '/'
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'From syccessfully submitted!')
        return super().form_valid(form)
    def form_invalid(self, form):

        return super().form_valid(form)
    def get_success_url(self):
        return reverse_lazy('homeview')

# class ContactView(View):
#     form_class = ContactForm
#     template_name = 'contact.html'
#     def get(self, request, *args, **kwargs):
#         form = self.form_class()
#         return render(request, self.template_name, {'form':form})
#
#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             form.save()
#             return HttpResponse("Success")
#         return render(request, self.template_name, {'form':form})


def contact(request):
    initials={
        'name':'My Name is ',
        'phone' : '+8801',
        'content': 'My Problem is'
    }
    if request.method == 'POST':
        form =ContactForm(request.POST,initial=initials)
        if form.is_valid():
            form.save()
    else:
        form =ContactForm(initial=initials)
    return render(request, 'contact.html',{'form':form})

class PostListView(ListView):
    template_name='tuition/postlist.html'
    queryset=Post.objects.all()
    model=Post
    context_object_name='posts'
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['posts'] = context.get('object_list')
        context['subjects'] = Subject.objects.all()
        context['classes'] = Class_in.objects.all()
        return context

def postview(request):
    post = Post.objects.all()
    return render(request, 'tuition/postview.html', {'post':post})

class PostDetailView(DetailView):
    model = Post
    template_name = 'tuition/postdetail.html'
    def get_context_data(self, *args, **kwargs):
        self.object.views.add(self.request.user)

        liked = False
        if self.object.likes.filter(id=self.request.user.id).exists():
            liked=True
        context = super().get_context_data(*args, **kwargs)
        post=context.get('object')
        comments=Comment.objects.filter(post=post.id, parent=None)
        replies=Comment.objects.filter(post=post.id).exclude(parent=None)
        DicofReply={}
        for reply in replies:
            if reply.parent.id not in DicofReply.keys():
                DicofReply[reply.parent.id]=[reply]
            else:
                DicofReply[reply.parent.id].append(reply)

        context['post'] = context.get('object')
        context['liked'] = liked
        context['comments'] = comments
        context['DicofReply'] = DicofReply
        # context['msg'] = 'This is post list'
        return context

def subview(request):
    sub = Subject.objects.get(name="Chamisty")
    post = sub.subject_set.all()
    return render(request, 'tuition/subjectview.html', {'sub':sub,'post':post})

class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'tuition/postcreate.html'
    # success_url = '/'
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    def get_success_url(self):
        # id = self.object.id
        return reverse_lazy('tuition:subjects')

class PostEditView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'tuition/postcreate.html'
    def get_success_url(self):
        id = self.object.id
        return reverse_lazy('tuition:postdetail', kwargs={'pk':id})

class PostDeleteView(DeleteView):
    model = Post
    template_name = "tuition/delete.html"
    success_url = reverse_lazy('tuition:postlist')

def commentdelete(request,id):
    comment=Comment.objects.get(id=id)
    comment.delete()
    return HttpResponse('Success')

def receiverchoose(j, obj):
    count = 0
    if j.district == obj.district:
        count = count + 1
    for i in j.medium:
        for k in obj.medium:
            if i==k:
                count=count + 1;
                break

    for i in j.subject.all():
        for k in obj.subject.all():
            if i==k:
                count=count + 1;
                break

    for i in j.class_in.all():
        for k in obj.class_in.all():
            if i==k:
                count=count + 1;
                break
    if count >= 3:
        return True

def postcreate(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            dis=form.cleaned_data['district']
            if not District.objects.filter(name=dis).exists():
                disobj=District(name=dis)
                disobj.save()
            sub = form.cleaned_data['subject']
            for i in sub:
                obj.subject.add(i)
                obj.save()
            class_in = form.cleaned_data['class_in']
            for i in class_in:
                obj.class_in.add(i)
                obj.save()
            us = TuitionProfile.objects.all()
            for i in us:
                if receiverchoose(i, obj):
                    receiver=i.user
                    if receiver!= request.user:
                        notify.send(request.user, recipient=receiver, verb=" He is searching a teacher like you" + f''' <a href="/tuition/postdetail/{obj.id}/"> go</a> ''')

            return HttpResponse("Success")
    else:
        form = PostForm(district_set=District.objects.all().order_by('name'))
    return render(request, 'tuition/postcreate.html', {'form':form})

import requests
import json
def postview(request):
    api_request=requests.get("https://jsonplaceholder.typicode.com/posts")
    try:
        api = json.loads(api_request.content)
    except :
        api = "Error"
    return render(request, 'tuition/postlistapi.html',{'api':api})

from django.http import HttpResponseRedirect

def likedpost(request, id):
    if request.method=="POST":
        post = Post.objects.get(id=id)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
            if request.user != post.user:
                notify.send(request.user, recipient=post.user, verb="has liked your post " + f'''<a href="/tuition/postdetail/{post.id}">Go</a>''')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def addcomment(request):
    if request.method == 'POST':
        comment=request.POST['comment']
        parentid=request.POST['parentid']
        postid=request.POST['postid']
        post = Post.objects.get(id=postid)
        if parentid:
            parent=Comment.objects.get(id=parentid)
            newcom = Comment(text=comment, user=request.user, post=post, parent=parent)
            newcom.save()
        else:
            newcom = Comment(text=comment, user=request.user, post=post)
            newcom.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def addphoto(request,id):
    post = Post.objects.get(id=id)
    if request.method=="POST":
        form=FileModelForm(request.POST, request.FILES)
        if form.is_valid():
            image=form.cleaned_data['image']
            obj=PostFile(image=image, post=post)
            obj.save()
            messages.success(request,'successfully uploaded image')
            return redirect(f"/tuition/postdetail/{id}/")
    else:
        form=FileModelForm()
    context={
        'form':form,
        'id': id,
    }
    return render(request, 'tuition/addphoto.html', context)

def apply(request, id):
    post = Post.objects.get(id=id)
    notify.send(request.user, recipient=post.user, verb="has applied for your tuition" + f'''<a href="/session/otherprofile/{request.user.username}/">See Profile</a>''')
    messages.success(request, 'You Have successfully applied for this tuition!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
