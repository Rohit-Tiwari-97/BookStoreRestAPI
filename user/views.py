import pyotp
from django.utils import timezone
from rest_framework.views import APIView
from .models import MyUser,MyUserProfile,Books,OtpModel
from .serializers import MyUserSerializer,MyUserProfileSerializer,OtpSerializer,BooksSerializer
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

def generate_otp(user_id):
    secret_key = pyotp.random_base32()
    totp = pyotp.TOTP(secret_key)
    otp = totp.now()
    try:
        otp_model = OtpModel.objects.get(otp_myuser=user_id)
        otp_model.otp_code = otp
        otp_model.save()
    except OtpModel.DoesNotExist:
        otp_serializer = OtpSerializer(data={'otp_myuser':user_id,'otp_code':otp})
        otp_serializer.is_valid(raise_exception=True)
        otp_serializer.save()

    return otp

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = MyUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(request.data['password'])
        user.save()
        otp = generate_otp(user.id)
        return Response({"message":"User Registered successfully","OTP":otp,
            "Next_step" : 'Please verify the otp to log in',
            "status" : status.HTTP_201_CREATED
          },status=201)  

   
       
class RegenrateOtpAPIView(APIView):
    def post(self, request):
        user = get_object_or_404(MyUser,email=request.data.get('email'))
        otp = generate_otp(user.id)
        return Response({"OTP":otp,"status":status.HTTP_200_OK})


class VerifyOtpAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user_otp = request.data.get('otp')
        user = get_object_or_404(MyUser, email=email)
        model_otp = get_object_or_404(OtpModel, otp_myuser=user)
        #model_otp = get_object_or_404(OtpModel.objects.filter(otp_myuser=user).order_by('-created_at')[:1])
        
        if model_otp.otp_code != user_otp:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        time_elapsed = timezone.now() - model_otp.updated_at
        if time_elapsed.total_seconds() > 60:
            return Response({'error': 'OTP has expired..!!, Please Regenerate the otp','time':time_elapsed}, status=status.HTTP_400_BAD_REQUEST)
    
        user.is_active = True
        user.save()
        return Response({'message': 'OTP verification successful..',"time":time_elapsed}, status=status.HTTP_200_OK) 

     
   
   

       
     
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
