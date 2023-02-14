from rest_framework.views import APIView
from .models import MyUser,MyUserProfile,Author,Books
from .serializers import MyUserSerializer,MyUserProfileSerializer,AuthorSerializer,BooksSerializer
from rest_framework.response import Response
from rest_framework import status,permissions
from django.contrib.auth import authenticate
from django.http import Http404,HttpResponse
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters



class CustomPagination(PageNumberPagination):
    page_size = 10
    





class RegisterAPIView(APIView):
    
    def post(self, request, format=None):
        data = request.data
        data['authors'] = []
        data['books'] = []
        serializer = MyUserSerializer(data=data)
        
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(data['password'])
        user.save()
        
        return Response({
            'status' : status.HTTP_201_CREATED,
            'message': 'User Registered Successfully',
          })

class LoginAPIView(APIView):
    
    def post(self, request, format=None): 
         
        email = request.data.get("email")
        password = request.data.get("password")
        try:
            user = authenticate(username=email, password=password)
            token, created  = Token.objects.get_or_create(user=user)
        except Exception:
            return Response({
                "error": "An error occurred while trying to authenticate the user or retrieve the token",
                "status":status.HTTP_400_BAD_REQUEST
                })
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

    
    '''def post(self, request, format=None): 

        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(username=email, password=password)
        token, created  = Token.objects.get_or_create(user=user)
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
                })'''

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

    permission_classes = [permissions.IsAuthenticated]
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


    def post(self,request, format=None):
        data = request.data
        data['myuser'] = request.user.id
        serializer = MyUserProfileSerializer(data=data)
        
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


class AuthorCreateAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):

        data = request.data
        data['owner'] = request.user.id
        serializer = AuthorSerializer(data=data)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response({
            'message': 'Author Created Successfully',
            'data': serializer.data
        })      


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
        try:
            author_to_update = Author.objects.get(pk=pk)
        except Author.DoesNotExist as e:
            raise Http404("Details not found") from e    
        if author_to_update.owner.id == request.user.id:
            data = request.data
            data['owner'] = request.user.id
            serializer = AuthorSerializer(instance=author_to_update,data=data)

            serializer.is_valid(raise_exception=True)

            serializer.save()

            return Response({
               'message': 'Author Updated Successfully',
               'data': serializer.data
            })

        return HttpResponse('403 Forbidden : You do not have permission to perform this action...', status=403)

    def delete(self, request, pk, format=None):
        try:
            author_to_delete =  Author.objects.get(pk=pk)
        except Author.DoesNotExist as e:
            raise Http404("Author Not found") from e
        if author_to_delete.owner.id != request.user.id:
            return HttpResponse('403 Forbidden : You do not have permission to perform this action...', status=403)
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

         userAuthors = list(request.user.authors.values_list('id',flat=True))    
         if author.id in userAuthors:
            data['author'] = author.id
            data['bookOwner'] = request.user.id
            serializer = BooksSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
             'message': 'Book Created Successfully',
             'data': serializer.data
              })
         

         return HttpResponse("Please Enter your authors_id only..",status=403)     

         

class BooksAPIView(ListAPIView):
    
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
        
        
        try:
            Book_to_update = Books.objects.get(pk=pk)
        except Books.DoesNotExist as e:
            raise Http404("Details not found") from e    

        if Book_to_update.bookOwner.id == request.user.id:
            data = request.data
            data['bookOwner'] = request.user.id
            serializer = BooksSerializer(instance=Book_to_update,data=data)

            serializer.is_valid(raise_exception=True)

            serializer.save()
            return Response({
            'message': 'Book Updated Successfully',
            'data': serializer.data
             })

        return HttpResponse('403 Forbidden : You do not have permission to perform this action...', status=403)

    def delete(self, request, pk, format=None):
        try:
            book_to_delete =  Books.objects.get(pk=pk)
        except Books.DoesNotExist as e:
            raise Http404("Author Not found") from e
        if book_to_delete.bookOwner.id != request.user.id:
            return HttpResponse('403 Forbidden : You do not have permission to perform this action...', status=403)
        book_to_delete.delete()
        return Response({
               'message': 'Book Deleted Successfully'
            }) 
