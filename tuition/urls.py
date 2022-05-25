from django.urls import path
from .views import *
from .forms import *
from .pdf import *

app_name = 'tuition'

urlpatterns = [
    # path('contact/', contact, name='contact'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('search/', search, name='search'),
    path('filter/', filter, name='filter'),
    path('pdf/', contact_pdf, name='pdf'),
    path('likepost/<int:id>/', likedpost, name='likepost'),
    path('addphoto/<int:id>/', addphoto, name='addphoto'),
    path('commentdelete/<int:id>/', commentdelete, name='commentdelete'),
    path('addcomment/', addcomment, name='addcomment'),
    path('postview/', postview, name='postview'),
    # path('contact2/', ContactView.as_view(form_class=ContactFormTwo, template_name='contact2.html'), name='contact2'),
    path('posts/', postview, name='posts'),
    path('postlist/', PostListView.as_view(), name='postlist'),
    path('delete/<int:pk>/', PostDeleteView.as_view(), name='delete'),
    path('postdetail/<int:pk>/', PostDetailView.as_view(), name='postdetail'),
    path('edit/<int:pk>/', PostEditView.as_view(), name='edit'),
    path('apply/<int:id>/', apply, name='apply'),
    path('subjects/', subview, name='subjects'),
    path('create/', postcreate, name='create'),
    # path('create/', PostCreateView.as_view(), name='create'),
]
