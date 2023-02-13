from rest_framework.views import APIView
from .models import MyUser,MyUserProfile,Author,Books
from .serializers import MyUserSerializer,MyUserProfileSerializer,AuthorSerializer,BooksSerializer
from rest_framework.response import Response
from rest_framework import status,permissions
from django.contrib.auth import authenticate
from django.http import Http404
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters



class CustomPagination(PageNumberPagination):
    page_size = 5
    





class RegisterAPIView(APIView):
    
    def post(self, request, format=None):
        data = request.data
        #email = request.data.get('email')
        #password = request.data.get('password')
        serializer = MyUserSerializer(data=data)
        
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(data['password'])
        user.save()
        response = Response()

        response.data = {
            'status' : status.HTTP_201_CREATED,
            'message': 'User Registered Successfully',
           }

        return response

class LoginAPIView(APIView):
    
    def post(self, request, format=None):  # sourcery skip: use-named-expression
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(username=email, password=password)
        token, created  = Token.objects.get_or_create(user=user)
        print(token)
        if user:    
            return Response(
                {
                "status":status.HTTP_200_OK, 
                "massage":"User Logged in succesfully..",
                "Token": token.key
                }
                )
        else:
            return Response({
                "error": "Wrong Credentials",
                "status":status.HTTP_400_BAD_REQUEST
                })

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

    permission_classes = [permissions.IsAdminUser]
    pagination_class = CustomPagination
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer      
       
class MyUserProfileAPIView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, format=None):
        data = MyUserProfile.objects.get(myuser=request.user.id)
        serializer = MyUserProfileSerializer(data)
        return Response(serializer.data) 


    def post(self,request, format=None):
        data = request.data
        data['myuser'] = request.user.id
        serializer = MyUserProfileSerializer(data=data)
        
        serializer.is_valid(raise_exception=True)
        serializer.save()

        serializer.data['myuser'] = request.user.email
        return Response({
            'status' : status.HTTP_201_CREATED,
            'message': 'UserProfile Updated Successfully',
            'Profile': serializer.data
        })


class AuthorCreateAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        data = request.data
        serializer = AuthorSerializer(data=data)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        response = Response()

        response.data = {
            'message': 'Author Created Successfully',
            'data': serializer.data
        }

        return response       


class AuthorDetailsAPIView(ListAPIView):

    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    

class SingleAuthorAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    # READ a single Author
    def get_object(self, pk):
        try:
            return Author.objects.get(pk=pk)
        except Author.DoesNotExist as e:
            raise Http404 from e

    def get(self, request, pk=None, format=None):

        data = self.get_object(pk)
        serializer = AuthorSerializer(data)   

        return Response(serializer.data)

   

    def put(self, request, pk=None, format=None):
        author_to_update = Author.objects.get(pk=pk)
        serializer = AuthorSerializer(instance=author_to_update,data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        response = Response()

        response.data = {
            'message': 'Author Updated Successfully',
            'data': serializer.data
        }

        return response

    def delete(self, request, pk, format=None):
        author_to_delete =  Author.objects.get(pk=pk)

        author_to_delete.delete()

        return Response({
            'message': 'Author Deleted Successfully'
        })


class BookCreateAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
         data = request.data
         author_id = request.data.get("author_id")
         try:
            author = Author.objects.get(id=author_id)
         except Author.DoesNotExist as e:
             raise Http404("Author does not exist") from e

         data['author'] = author_id

         serializer = BooksSerializer(data=data)

         serializer.is_valid(raise_exception=True)

         serializer.save()

         response = Response()

         response.data = {
             'message': 'Book Created Successfully',
             'data': serializer.data
         }

         return response

class BookDetailsAPIView(ListAPIView):
    
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination
    queryset = Books.objects.all()
    serializer_class = BooksSerializer
    filter_backends = [DjangoFilterBackend,filters.SearchFilter]
    filterset_fields = ['publishDate']
    search_fields = ['title']

class SingleBookAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    # READ a single Book
    def get_object(self, pk):
        try:
            return Books.objects.get(pk=pk)
        except Books.DoesNotExist as e:
            raise Http404 from e

    def get(self, request, pk=None, format=None):
        data = self.get_object(pk)
        serializer = BooksSerializer(data)   

        return Response(serializer.data)

   

    def put(self, request, pk=None, format=None):
        Book_to_update = Books.objects.get(pk=pk)
        serializer = BooksSerializer(instance=Book_to_update,data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        response = Response()

        response.data = {
            'message': 'Book Updated Successfully',
            'data': serializer.data
        }

        return response

    def delete(self, request, pk, format=None):
        Book_to_delete =  Books.objects.get(pk=pk)

        Book_to_delete.delete()

        return Response({
            'message': 'Book Deleted Successfully'
        })