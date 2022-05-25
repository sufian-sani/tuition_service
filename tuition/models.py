from django.db import models
from django.utils.timezone import now
from PIL import Image
from django.utils.text import slugify
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User

# Create your models here.
class PostManager(models.Manager):
    def sorted(self, title):
        return self.order_by(title)
    def less_than(self, size):
        return self.filter(salary__lt=size)


class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=17)
    content = models.TextField()

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

    def get_total_post(self):
        return self.subject_set.all().count()

    def get_post_list(self):
        return self.subject_set.all()

class Class_in(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class District(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    slug = models.CharField(max_length=100, default=title)
    email = models.EmailField()
    salary = models.FloatField()
    details = models.TextField()
    available = models.BooleanField()
    CATEGORY = (
        ('Teacher','Teacher'),
        ('Student', 'Student'),
    )
    category = models.CharField(max_length=100, choices=CATEGORY)
    created_at = models.DateTimeField(default=now)
    image = models.ImageField(default='default.jpg', upload_to='tuition/images')

    MEDIUM = (
        ('bangla','bangla'),
        ('English','English'),
        ('Urdu','Urdu'),
        ('Hindi','Hindi'),
        ('Arabic','Arabic'),
    )
    medium = MultiSelectField(max_length=100, max_choices=5, choices=MEDIUM, default='bangla')
    subject = models.ManyToManyField(Subject, related_name='subject_set')
    class_in = models.ManyToManyField(Class_in, related_name='class_set')
    district=models.CharField(max_length=100, null=True, blank=True)
    likes = models.ManyToManyField(User, related_name='post_likes')
    views = models.ManyToManyField(User, related_name='post_views')
    def total_likes(self):
        return self.likes.count()
    def total_views(self):
        return self.views.count()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300,300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def get_subject_list(self):
        sub = self.subject.all()
        subjects = ""
        for s in sub:
            subjects = subjects + str(s.name) + ","
        return subjects

    def get_class_list(self):
        sub = self.class_in.all()
        subjects = ""
        for s in sub:
            subjects = subjects + str(s.name) + ","
        return subjects

    def propercase(self):
        return self.title.title()

    def uppercase(self):
        return self.title.upper()

    def details_short(self):
        details_words = self.details.split(' ')
        if len(details_words) > 10:
            return ' '.join(details_words[:10]) + "...."
        else:
            return self.details

    def __str__(self):
        return self.title + ": by " +self.user.username

    objects=models.Manager()
    items = PostManager()

class PostFile(models.Model):
    image = models.ImageField(upload_to="tuition/images")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    def save(self, *args, **kwargs):
        super(PostFile, self).save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(default=now)
    def __str__(self):
        return self.user.username + ": " + self.text[0:15]
