from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from .models import Loan, Book, Category
import re


# Validateurs

def validate_isbn(value):
    """Valide le format ISBN-13"""
    isbn = value.replace('-', '').replace(' ', '')
    if not re.match(r'^\d{13}$', isbn):
        raise ValidationError('Le code ISBN doit contenir exactement 13 chiffres.')


def validate_library_card(value):
    """Valide le format du numéro de carte de bibliothèque"""
    if not re.match(r'^\d{8}$', value):
        raise ValidationError('Le numéro de carte doit contenir exactement 8 chiffres.')


# Loans

class LoanForm(forms.ModelForm):
    """Formulaire pour créer un nouvel emprunt"""
    
    class Meta:
        model = Loan
        fields = ['book', 'borrower_name', 'borrower_email', 'borrower_card_number', 'comments']
        widgets = {
            'book': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'borrower_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom complet de l\'emprunteur',
                'required': True
            }),
            'borrower_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemple.fr',
                'required': True
            }),
            'borrower_card_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345678',
                'required': True,
                'maxlength': 8
            }),
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Commentaires optionnels...'
            }),
        }
        labels = {
            'book': 'Livre à emprunter',
            'borrower_name': 'Nom de l\'emprunteur',
            'borrower_email': 'Email de l\'emprunteur',
            'borrower_card_number': 'Numéro de carte de bibliothèque',
            'comments': 'Commentaires',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtre pour n'afficher que les livres disponibles
        self.fields['book'].queryset = Book.objects.filter(
            copies_available__gt=0
        ).select_related('author', 'category')
        # Message d'aide personnalisé
        self.fields['book'].help_text = 'Seuls les livres disponibles sont affichés'
        self.fields['borrower_card_number'].validators.append(validate_library_card)
    
    def clean_borrower_email(self):
        """Validation personnalisée de l'email"""
        email = self.cleaned_data.get('borrower_email')
        if email and not email.endswith(('.fr', '.com', '.org')):
            raise ValidationError('L\'email doit se terminer par .fr, .com ou .org')
        return email
    
    def clean_borrower_card_number(self):
        """Validation du numéro de carte"""
        card_number = self.cleaned_data.get('borrower_card_number')
        if card_number and not card_number.isdigit():
            raise ValidationError('Le numéro de carte ne doit contenir que des chiffres.')
        return card_number
    
    def clean(self):
        """Validation globale du formulaire"""
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        card_number = cleaned_data.get('borrower_card_number')
        
        # Vérification de la disponibilité du livre
        if book and book.copies_available <= 0:
            raise ValidationError(f'Le livre "{book.title}" n\'est plus disponible.')
        
        # Vérification de la limite de 5 emprunts par usager
        if card_number:
            active_loans = Loan.objects.filter(
                borrower_card_number=card_number,
                status__in=[Loan.STATUS_ACTIVE, Loan.STATUS_PENDING]
            ).count()
            
            if active_loans >= 5:
                raise ValidationError(
                    f'L\'usager avec la carte {card_number} a déjà 5 emprunts actifs. '
                    'La limite maximale est atteinte.'
                )
        
        return cleaned_data


# Recherche de livres

class BookSearchForm(forms.Form):
    """Formulaire de recherche avancée de livres"""
    
    title = forms.CharField(
        required=False,
        label='Titre du livre',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par titre...'
        })
    )
    
    author = forms.CharField(
        required=False,
        label='Auteur',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom de l\'auteur...'
        })
    )
    
    category = forms.ModelChoiceField(
        required=False,
        label='Catégorie',
        queryset=Category.objects.all(),
        empty_label='Toutes les catégories',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    isbn = forms.CharField(
        required=False,
        label='ISBN',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Code ISBN...'
        })
    )
    
    available_only = forms.BooleanField(
        required=False,
        label='Livres disponibles uniquement',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    year_min = forms.IntegerField(
        required=False,
        label='Année min',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1900',
            'min': 1450,
            'max': date.today().year
        })
    )
    
    year_max = forms.IntegerField(
        required=False,
        label='Année max',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': str(date.today().year),
            'min': 1450,
            'max': date.today().year
        })
    )
    
    def clean(self):
        """Validation des années"""
        cleaned_data = super().clean()
        year_min = cleaned_data.get('year_min')
        year_max = cleaned_data.get('year_max')
        
        if year_min and year_max and year_min > year_max:
            raise ValidationError('L\'année minimale ne peut pas être supérieure à l\'année maximale.')
        
        return cleaned_data


# Contact

class ContactForm(forms.Form):
    """Formulaire de contact"""
    
    name = forms.CharField(
        max_length=100,
        label='Nom complet',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre nom complet'
        })
    )
    
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre.email@exemple.fr'
        })
    )
    
    subject = forms.CharField(
        max_length=200,
        label='Sujet',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Objet de votre message'
        })
    )
    
    message = forms.CharField(
        label='Message',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Votre message...'
        })
    )
    
    def clean_message(self):
        """Validation du message"""
        message = self.cleaned_data.get('message')
        if message and len(message) < 10:
            raise ValidationError('Le message doit contenir au moins 10 caractères.')
        return message


# Retour de livre

class ReturnBookForm(forms.Form):
    """Formulaire pour marquer un livre comme retourné"""
    
    loan_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    
    comments = forms.CharField(
        required=False,
        label='Commentaires de retour',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'État du livre, remarques...'
        })
    )
    
    def clean_loan_id(self):
        """Vérification que l'emprunt existe"""
        loan_id = self.cleaned_data.get('loan_id')
        try:
            loan = Loan.objects.get(pk=loan_id)
            if loan.status == Loan.STATUS_RETURNED:
                raise ValidationError('Ce livre a déjà été retourné.')
        except Loan.DoesNotExist:
            raise ValidationError('Cet emprunt n\'existe pas.')
        return loan_id
