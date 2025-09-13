from django.contrib import admin
from import_export.admin import ExportMixin
from .models import QuoteRequest, CustomUser, TourDate, TourPackage
from django.contrib.auth.admin import UserAdmin


@admin.register(QuoteRequest)
class QuoteRequestAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'destination', 'departure', 'special_request', 'timestamp']

    def special_request(self, obj):
        return obj.message

    special_request.short_description = 'Special Request'

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'phone', 'name', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'phone', 'name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'phone', 'password')}),
        ('Personal info', {'fields': ('name','dob')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'name', 'password1', 'password2'),

        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)


# admin.site.register(TourPackage)



# 3. TourDate Inline for TourPackage
class TourDateInline(admin.TabularInline):
    model = TourDate
    extra = 1


# 4. TourPackage Admin with inline TourDates
@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'destination', 'duration', 'price']
    inlines = [TourDateInline]


# Optional: Register TourDate separately if needed
@admin.register(TourDate)
class TourDateAdmin(admin.ModelAdmin):
    list_display = ['tour', 'date', 'seats_available']
    list_filter = ['tour']