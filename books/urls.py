from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    # home page
    path('', views.home, name='home'),
    
    # Books
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('category/<int:pk>/', views.books_by_category, name='category_books'),
    
    # Authors
    path('authors/', views.author_list, name='author_list'),
    path('authors/<int:pk>/', views.author_detail, name='author_detail'),
    
    # Loans
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/overdue/', views.overdue_loans, name='overdue_loans'),
    
    # Static
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
