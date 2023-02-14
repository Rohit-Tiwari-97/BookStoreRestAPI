from django.urls import path
from .views import (RegisterAPIView,
LoginAPIView,
MyUserDataAPIView,
MyUserProfileAPIView,
AuthorCreateAPIView,
AuthorDetailsAPIView,
SingleAuthorAPIView,
BookCreateAPIView,
BooksAPIView,
SingleBookAPIView,
LogoutAPIView
)

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),   
    path('login/', LoginAPIView.as_view()),         
    path('data/', MyUserDataAPIView.as_view()),
    path('profile/', MyUserProfileAPIView.as_view()),
    path('createauthor/', AuthorCreateAPIView.as_view()),
    path('authors/', AuthorDetailsAPIView.as_view()),             
    path('authors/<int:pk>/', SingleAuthorAPIView.as_view()),   # FOR Reading, Updating, Deleting the authors
    path('createbook/', BookCreateAPIView.as_view()),        
    path('books/', BooksAPIView.as_view()),
    path('books/<int:pk>/', SingleBookAPIView.as_view()),   # FOR Reading, Updating, Deleting the books
    path('logout/', LogoutAPIView.as_view()),
]