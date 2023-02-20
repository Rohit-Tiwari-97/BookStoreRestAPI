from rest_framework import serializers
from user.models import MyUser,MyUserProfile,OtpModel,Books



class MyUserSerializer(serializers.ModelSerializer):
    #books = serializers.PrimaryKeyRelatedField(many=True, queryset=Books.objects.all())
    class Meta:
        model = MyUser
        fields = ['id','email','userRole','created_at','is_active','is_admin']


class MyUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUserProfile   
        fields = '__all__'

class OtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtpModel
        fields = '__all__'   

class BooksSerializer(serializers.ModelSerializer):
    #author = serializers.PrimaryKeyRelatedField(queryset=MyUser.objects.all())
    
    class Meta:
        model = Books      
        fields = ['id','title', 'isbn', 'description', 'publishDate', 'is_available','author']
        


       