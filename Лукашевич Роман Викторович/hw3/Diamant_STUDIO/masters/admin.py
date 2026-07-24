from django.contrib import admin
from .models import Master, MasterPortFolioImage

class MasterPortfolioImageInline(admin.TabularInline):
    model = MasterPortFolioImage
    extra = 3

@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "specialization",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "specialization",
    )

    ordering = (
        "name",
    )

    filter_horizontal = ('services',) 

    inlines = [MasterPortfolioImageInline]

    admin.site.register(MasterPortFolioImage)   