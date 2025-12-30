from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .forms import LoanForm, BookSearchForm, ContactForm, ReturnBookForm
from django.db.models import Q
from django.contrib import messages
from datetime import date
from .models import Book, Author, Category, Loan
from datetime import timedelta

# home page

def home(request):
    """Page d'accueil avec statistiques"""
    recent_books = Book.objects.all().select_related('author', 'category').order_by('-added_at')[:6]
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
        'is_available': book.copies_available > 0,
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
    status_filter = request.GET.get('status', Loan.STATUS_ACTIVE)
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
        status__in=[Loan.STATUS_ACTIVE, Loan.STATUS_LATE],
        due_at__lt=timezone.now()
    ).select_related('book', 'book__author').order_by('due_at')
    
    context = {'loans': loans}
    return render(request, 'overdue_loans.html', context)

# Static

def about(request):
    """Page À propos"""
    return render(request, 'about.html')


def contact(request):
    """Page de contact"""
    return render(request, 'contact.html')


def create_loan(request):
    """Création d'un nouvel emprunt"""
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            # Définir la date limite à 14 jours
            loan.due_at = timezone.now() + timedelta(days=14)
            loan.status = Loan.STATUS_ACTIVE
            loan.save()
            
            # Décrémenter les exemplaires disponibles
            loan.book.copies_available -= 1
            loan.book.save()
            
            messages.success(request, f'Emprunt créé avec succès pour "{loan.book.title}".')
            return redirect('books:loan_list')
    else:
        form = LoanForm()
    
    context = {'form': form}
    return render(request, 'loan_form.html', context)


def return_book(request, loan_id):
    """Marquer un livre comme retourné"""
    loan = get_object_or_404(Loan, pk=loan_id)
    
    if loan.status == Loan.STATUS_RETURNED:
        messages.warning(request, 'Ce livre a déjà été retourné.')
        return redirect('books:loan_list')
    
    if request.method == 'POST':
        form = ReturnBookForm(request.POST)
        if form.is_valid():
            # Marquer comme retourné
            loan.returned_at = timezone.now()
            loan.status = Loan.STATUS_RETURNED
            if form.cleaned_data.get('comments'):
                loan.comments = form.cleaned_data['comments']
            loan.save()
            
            # Libérer un exemplaire
            loan.book.copies_available += 1
            loan.book.save()
            
            messages.success(request, f'Le livre "{loan.book.title}" a été retourné.')
            return redirect('books:loan_list')
    else:
        form = ReturnBookForm(initial={'loan_id': loan_id})
    
    context = {
        'form': form,
        'loan': loan,
    }
    return render(request, 'return_book.html', context)


def book_search(request):
    """Recherche avancée de livres"""
    form = BookSearchForm(request.GET or None)
    books = Book.objects.all().select_related('author', 'category')
    
    if form.is_valid():
        # Filtrage par titre
        if form.cleaned_data.get('title'):
            books = books.filter(title__icontains=form.cleaned_data['title'])
        
        # Filtrage par auteur
        if form.cleaned_data.get('author'):
            books = books.filter(
                Q(author__first_name__icontains=form.cleaned_data['author']) |
                Q(author__last_name__icontains=form.cleaned_data['author'])
            )
        
        # Filtrage par catégorie
        if form.cleaned_data.get('category'):
            books = books.filter(category=form.cleaned_data['category'])
        
        # Filtrage par ISBN
        if form.cleaned_data.get('isbn'):
            books = books.filter(isbn__icontains=form.cleaned_data['isbn'])
        
        # Filtrage par disponibilité
        if form.cleaned_data.get('available_only'):
            books = books.filter(copies_available__gt=0)
        
        # Filtrage par année
        if form.cleaned_data.get('year_min'):
            books = books.filter(publication_year__gte=form.cleaned_data['year_min'])
        
        if form.cleaned_data.get('year_max'):
            books = books.filter(publication_year__lte=form.cleaned_data['year_max'])
    
    # Pagination
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
    }
    return render(request, 'book_search.html', context)


def contact_view(request):
    """Vue du formulaire de contact"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            messages.success(
                request, 
                f'Merci {name} ! Votre message a été envoyé avec succès. '
                'Nous vous répondrons dans les plus brefs délais.'
            )
            return redirect('books:home')
    else:
        form = ContactForm()
    
    context = {'form': form}
    return render(request, 'contact.html', context)