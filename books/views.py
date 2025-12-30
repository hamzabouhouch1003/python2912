from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from datetime import date
from .models import Book, Author, Category, Loan

# home page

def home(request):
    """Page d'accueil avec statistiques"""
    recent_books = Book.objects.all().select_related('author', 'category').order_by('-created_at')[:6]
    total_books = Book.objects.count()
    total_authors = Author.objects.count()
    active_loans = Loan.objects.filter(status='BORROWED').count()
    
    context = {
        'recent_books': recent_books,
        'total_books': total_books,
        'total_authors': total_authors,
        'active_loans': active_loans,
    }
    return render(request, 'home.html', context)


# Books

def book_list(request):
    """Liste paginée de tous les livres avec recherche"""
    books = Book.objects.all().select_related('author', 'category')
    
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__first_name__icontains=search_query) |
            Q(author__last_name__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    category_id = request.GET.get('category')
    if category_id:
        books = books.filter(category_id=category_id)
    
    paginator = Paginator(books, 12)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'categories': categories,
        'selected_category': category_id,
    }
    return render(request, 'book_list.html', context)


def book_detail(request, pk):
    """Détail d'un livre avec informations complètes"""
    book = get_object_or_404(Book.objects.select_related('author', 'category'), pk=pk)
    active_loans = book.loans.filter(status='BORROWED')
    
    context = {
        'book': book,
        'active_loans': active_loans,
        'is_available': book.available_copies > 0,
    }
    return render(request, 'book_detail.html', context)


def books_by_category(request, pk):
    """Liste des livres d'une catégorie"""
    category = get_object_or_404(Category, pk=pk)
    books = category.books.all().select_related('author')
    
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'category_books.html', context)


# Authors

def author_list(request):
    """Liste de tous les auteurs"""
    search_query = request.GET.get('search', '')
    authors = Author.objects.all()
    
    if search_query:
        authors = authors.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    authors = authors.order_by('last_name', 'first_name')
    
    paginator = Paginator(authors, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'author_list.html', context)


def author_detail(request, pk):
    """Détail d'un auteur avec liste de ses ouvrages"""
    author = get_object_or_404(Author, pk=pk)
    books = author.books.all().select_related('category')
    
    context = {
        'author': author,
        'books': books,
    }
    return render(request, 'author_detail.html', context)


# Loans

def loan_list(request):
    """Liste des emprunts avec filtres"""
    status_filter = request.GET.get('status', 'BORROWED')
    loans = Loan.objects.filter(status=status_filter).select_related('book', 'book__author')
    
    paginator = Paginator(loans, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
    }
    return render(request, 'loan_list.html', context)


def overdue_loans(request):
    """Liste des emprunts en retard"""
    loans = Loan.objects.filter(
        status='BORROWED',
        due_date__lt=date.today()
    ).select_related('book', 'book__author').order_by('due_date')
    
    context = {'loans': loans}
    return render(request, 'overdue_loans.html', context)


# Static

def about(request):
    """Page À propos"""
    return render(request, 'about.html')


def contact(request):
    """Page de contact"""
    return render(request, 'contact.html')
