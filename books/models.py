from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

def validate_publication_year(year: int):
    current_year = timezone.now().year
    if year < 1450 or year > current_year:
        raise ValidationError(
            f"L'année de publication doit être entre 1450 et {current_year}."
        )

class Author(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    biography = models.TextField(blank=True)
    death_date = models.DateField(null=True, blank=True)
    website = models.URLField(blank=True)
    photo = models.ImageField(upload_to="authors/", blank=True, null=True)

    class Meta:
        unique_together = ("first_name", "last_name")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    publication_year = models.IntegerField(validators=[validate_publication_year])
    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,      # empêche la suppression d'un auteur avec livres
        related_name="books",          # relation inverse : author.books.all()
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="books",
    )
    copies_available = models.PositiveIntegerField(default=0)
    copies_total = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=50, blank=True)
    pages = models.PositiveIntegerField(null=True, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    cover_image = models.ImageField(upload_to="books/", blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.copies_available > self.copies_total:
            raise ValidationError(
                "Les exemplaires disponibles ne peuvent pas dépasser le total."
            )

    def __str__(self):
        return self.title

class Loan(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ACTIVE = "active"
    STATUS_RETURNED = "returned"
    STATUS_LATE = "late"

    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_ACTIVE, "En cours"),
        (STATUS_RETURNED, "Retourné"),
        (STATUS_LATE, "En retard"),
    ]

    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name="loans",
    )
    borrower_name = models.CharField(max_length=255)
    borrower_email = models.EmailField()
    borrower_card_number = models.CharField(max_length=50)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"{self.book.title} → {self.borrower_name}"

    @property
    def is_overdue(self):
        return (
            self.status in {self.STATUS_ACTIVE, self.STATUS_LATE}
            and self.due_at < timezone.now()
        )


