import pyotp
from rest_framework.views import APIView
from .models import MyUser,MyUserProfile,Books
from .serializers import MyUserSerializer,MyUserProfileSerializer,BooksSerializer
from rest_framework.response import Response
from rest_framework import status,permissions
from django.contrib.auth import authenticate
from django.http import Http404
from .permissions import IsAuthorOrReadOnly
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class CustomPagination(PageNumberPagination):
    page_size = 5
    
class RegisterAPIView(APIView):
    def post(self, request):
        serializer = MyUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        secret_key = pyotp.random_base32()
        totp = pyotp.TOTP(secret_key, interval = 180)
        otp = totp.now()
        request.session['secret_key'] = secret_key
        request.session['data'] = request.data
    
        return Response({
            "OTP": otp,
            "Next_step" : 'Please verify the otp to complete the registration.',
            "status" : status.HTTP_200_OK
          })

class VerifyOtpAPIView(APIView):
    def post(self, request):
        secret = request.session.get('secret_key')
        otp = request.data.get('otp')
        data =  request.session.get('data')
        if secret and otp:
            return self.verify_otp(secret, otp, data)
        return Response("Secret code not found",status=400)  

     
    def verify_otp(self, secret, otp, data):
        totp = pyotp.TOTP(secret, interval = 180)
        is_valid = totp.verify(otp)

        if is_valid  is True:
            return self.createmyuser(data, is_valid)
        return Response({'message': 'OTP Verification Failed..!!, Please regenrate the OTP', "OTP_is_valid":is_valid,"status":status.HTTP_403_FORBIDDEN},status=403)

    def createmyuser(self, data, is_valid):
        serializer = MyUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(data['password'])
        user.is_active = True
        user.save()
        return Response({'message': 'OTP Verification Successfull..!!, User Registered Successfully', "OTP_is_valid":is_valid,"status":status.HTTP_201_CREATED})
     
class LoginAPIView(APIView):
    
    def post(self, request, format=None): 

        email = request.data.get("email")
        password = request.data.get("password")
        if user := authenticate(username=email, password=password):
            token, _  = Token.objects.get_or_create(user=user)
            return Response(
                {
                "status":status.HTTP_200_OK, 
                "massage":"User Logged in succesfully..",
                "Token": token.key
                }
                )
        return Response({
                "error": "Wrong Credentials",
                "status":status.HTTP_400_BAD_REQUEST,
                },status=400)

class LogoutAPIView(APIView):
    
    permission_classes = [permissions.IsAuthenticated] 
    def post(self, request, format=None):
        user = request.user
        user.auth_token.delete()
        return Response({
                "message": "User Logout Successfully",
                "status": status.HTTP_200_OK
                })
        
class MyUserDataAPIView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]
    pagination_class = CustomPagination
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer      
       
class MyUserProfileAPIView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, format=None):
        try:
            data = MyUserProfile.objects.get(myuser=request.user.id)
        except MyUserProfile.DoesNotExist as e:
            raise Http404("Details not found") from e
        serializer = MyUserProfileSerializer(data)
        return Response(serializer.data) 


    def post(self,request):
        request.data['myuser'] = request.user.id
        serializer = MyUserProfileSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'status' : status.HTTP_201_CREATED,
            'message': 'UserProfile Created Successfully',
            'Profile': serializer.data
        })

    
    def put(self, request, format=None):
        profile_to_update = MyUserProfile.objects.get(myuser=request.user.id)
        serializer = MyUserProfileSerializer(instance = profile_to_update, data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response({
            'message': 'User Updated Successfully',
            'data': serializer.data
        }) 

class AuthorDetailsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]
    def get(self, request):
        data = MyUser.objects.filter(userRole='Author')
        serializer = MyUserSerializer(data,many=True)
        return Response(serializer.data)

class DeleteAuthorAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser]
    def delete(self, request, pk=None):
        author_to_delete = get_object_or_404(MyUser.objects.filter(userRole='Author'), pk=pk)
        author_to_delete.delete()
        return Response({
               'message': 'Author Deleted Successfully'
                })    
   
class BookCreateAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated,(IsAuthorOrReadOnly|permissions.IsAdminUser)]
   
    def post(self, request):
        request.data['author'] = request.user.id
        serializer = BooksSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'Book Created Successfully',
            'data': serializer.data
        })
                    
class BooksAPIView(ListAPIView):
    
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    queryset = Books.objects.filter(is_available=True)
    serializer_class = BooksSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['publishDate']
    search_fields = ['title']
   
class BookGetUpdateAPIView(APIView):
    
    permission_classes = [permissions.IsAuthenticated,(IsAuthorOrReadOnly|permissions.IsAdminUser)]

    def get(self,request,pk=None):
        serializer = BooksSerializer(get_object_or_404(Books.objects.filter(is_available=True), pk=pk))   
        return Response(serializer.data)

    def put(self, request, pk=None):
        book_to_update = get_object_or_404(Books, pk=pk)
        serializer = BooksSerializer(instance=book_to_update, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'Book Updated Successfully',
            'data': serializer.data
             })
          
class AuthorBookDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAuthorOrReadOnly]
    def delete(self, request, pk=None):
        book_to_delete = get_object_or_404(Books, pk=pk)
        book_to_delete.delete()
        return Response({
               'message': 'Book Deleted Successfully'
               })           
      
class AdminBookDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,permissions.IsAdminUser] 
    def delete(self, request, pk=None):
        book_to_delete = get_object_or_404(Books, pk=pk)
        book_to_delete.is_available = False
        book_to_delete.save()
        return Response({
               'message': 'Book Deleted Successfully'
               })       
