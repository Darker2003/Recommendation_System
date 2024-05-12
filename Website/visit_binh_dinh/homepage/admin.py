from django.contrib import admin
from .models import locationdatabase, userdatabase, userlocationlogging, usersearchlogging
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = userdatabase
    
    list_display = ("username", "email", "is_staff", "is_superuser", "is_active")
    list_filter = ("username", "email", "is_staff", "is_superuser", "is_active")
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_superuser", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "email", "password1", "password2", "is_staff",
                "is_superuser", "is_active", "groups", "user_permissions"
            )}
        ),
    )
    search_fields = ("username", "email",)
    ordering = ("username", "email",)

# Register your models here.
admin.site.register(locationdatabase)
admin.site.register(userdatabase, CustomUserAdmin)
admin.site.register(userlocationlogging)
admin.site.register(usersearchlogging)