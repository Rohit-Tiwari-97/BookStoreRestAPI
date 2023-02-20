from django.contrib import admin
from .models import MyUser,MyUserProfile,OtpModel,Books

admin.site.register(MyUser)
admin.site.register(MyUserProfile)
admin.site.register(OtpModel)
admin.site.register(Books)