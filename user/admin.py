from django.contrib import admin
from .models import MyUser,MyUserProfile,Books

admin.site.register(MyUser)
admin.site.register(MyUserProfile)
admin.site.register(Books)