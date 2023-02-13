from rest_framework import serializers
from user.models import MyUser,MyUserProfile,Author,Books

#from django.contrib.auth import get_user_model
#MyUser = get_user_model()


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = '__all__'


class MyUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUserProfile
        fields = '__all__'


class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Author
        fields = '__all__'



class BooksSerializer(serializers.ModelSerializer):


    class Meta:
        model = Books        
        fields = '__all__'

       