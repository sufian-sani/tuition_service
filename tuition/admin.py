from django.contrib import admin
from .models import *
from django.utils import timezone
from django.utils.html import format_html
# Register your models here.

admin.site.site_header = 'TuitionBD Admin Panel'
admin.site.site_title = 'TuitionBD Admin Panel'
admin.site.index_title = ''

class CommentInline(admin.TabularInline):
    model=Comment

class PostFileInline(admin.TabularInline):
    model=PostFile

class PostAdmin(admin.ModelAdmin):
    # fields = ('user', 'title')
    exclude = ('user', 'title')
    readonly_fields = ('slug',)
    list_display = ('user', 'title_html_display', 'title', 'created_at', 'get_subjects','get_class_in' , 'salary','created_since',)
    list_filter = ('user', 'subject', 'class_in')
    search_fields = ('details', 'user__username', 'subject__name', 'class_in__name')
    filter_horizontal= ('subject','class_in')
    list_editable = ('salary',)
    list_display_links = ('title',)
    actions = ('change_salary_3000',)
    inlines = [
        CommentInline,
        PostFileInline,
    ]
    # inlines=[
    #     CommentInline,
    #     PostFileInline,
    # ]
    #
    def title_html_display(self, obj):
        return format_html(
            f'<span style="font-size: 20px; color:blue;"> {obj.title}</span>'
        )

    def created_since(self, Post):
        diff = timezone.now() - Post.created_at
        return diff.days
    created_since.short_description = ' Since Created'
    #
    def get_subjects(self, obj):
        return ", ".join([p.name for p in obj.subject.all()])
    get_subjects.short_description = 'Subjects'
    #
    def get_class_in(self, obj):
        return ", ".join([p.name for p in obj.class_in.all()])
    get_class_in.short_description = 'Class'

    def change_salary_3000(self, request, queryset):
        count = queryset.update(salary=3000.0)
        self.message_user(request, '{} posts updated'.format(count))
    change_salary_3000.short_description='Change Salary'

admin.site.register(Contact)
admin.site.register(Post, PostAdmin)
admin.site.register(Subject)
admin.site.register(Class_in)
admin.site.register(Comment)
admin.site.register(PostFile)
admin.site.register(District)
