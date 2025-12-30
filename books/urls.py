from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    # home page
    path('', views.home, name='home'),
    
    # Books
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/search/', views.book_search, name='book_search'),  
    path('category/<int:pk>/', views.books_by_category, name='category_books'),
    
    # Authors
    path('authors/', views.author_list, name='author_list'),
    path('authors/<int:pk>/', views.author_detail, name='author_detail'),
    
    # Loans
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/create/', views.create_loan, name='create_loan'),  
    path('loans/<int:loan_id>/return/', views.return_book, name='return_book'),  
    path('loans/overdue/', views.overdue_loans, name='overdue_loans'),
    
    # Static
    path('about/', views.about, name='about'),
    path('contact/', views.contact_view, name='contact'),  
]
