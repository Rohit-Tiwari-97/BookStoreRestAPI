from rest_framework import serializers
from user.models import MyUser,MyUserProfile,Author,Books



class MyUserSerializer(serializers.ModelSerializer):
    authors = serializers.PrimaryKeyRelatedField(many=True, queryset=Author.objects.all())
    books = serializers.PrimaryKeyRelatedField(many=True, queryset=Books.objects.all())
    class Meta:
        model = MyUser
        fields = ['id','email','userRole','created_at','is_active','is_admin','authors','books']


class MyUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUserProfile
        fields = '__all__'


class AuthorSerializer(serializers.ModelSerializer):
    owner =  serializers.PrimaryKeyRelatedField(queryset=MyUser.objects.all())
    class Meta:
        model = Author
        fields = ["id","name","email","bio","owner"]



class BooksSerializer(serializers.ModelSerializer):
    bookOwner = serializers.PrimaryKeyRelatedField(queryset=MyUser.objects.all())
    
    class Meta:
        model = Books        
        fields = ['id','title','isbn','description','publishDate','author','bookOwner']

       