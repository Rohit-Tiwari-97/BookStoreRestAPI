from django.contrib import admin
from .models import MyUser,MyUserProfile, Author,Books

admin.site.register(MyUser)
admin.site.register(MyUserProfile)
admin.site.register(Author)
admin.site.register(Books)