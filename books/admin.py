from django.contrib import admin
from django.utils import timezone
from .models import Author, Book, Category, Loan

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "description"]

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["last_name", "first_name", "nationality", "birth_date"]
    list_filter = ["nationality"]
    search_fields = ["first_name", "last_name"]

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ["book", "borrower_name", "borrowed_at", "due_at", "status"]
    list_filter = ["status", "borrowed_at", "due_at"]
    search_fields = ["borrower_name", "borrower_email", "borrower_card_number"]
    actions = ["mark_as_returned"]

    def mark_as_returned(self, request, queryset):
        for loan in queryset:
            loan.status = Loan.STATUS_RETURNED
            loan.returned_at = timezone.now()
            loan.save()
    mark_as_returned.short_description = "Marquer comme retourné"


class LoanInline(admin.TabularInline):
    model = Loan
    extra = 0
    fields = ["borrower_name", "borrowed_at", "due_at", "status"]
    readonly_fields = ["borrower_name", "borrowed_at", "due_at", "status"]
    can_delete = False

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "isbn",
        "category",
        "copies_available",
        "copies_total",
    ]
    list_filter = ["category", "author", "publication_year"]
    search_fields = ["title", "isbn", "author__first_name", "author__last_name"]
    readonly_fields = ["added_at"]
    inlines = [LoanInline]

    fieldsets = (
        ("Informations générales", {
            "fields": ("title", "author", "category", "description"),
        }),
        ("Publication", {
            "fields": ("isbn", "publication_year", "publisher", "language", "pages"),
        }),
        ("Stock", {
            "fields": ("copies_total", "copies_available"),
        }),
        ("Médias", {
            "fields": ("cover_image",),
        }),
        ("Meta", {
            "fields": ("added_at",),
        }),
    )
