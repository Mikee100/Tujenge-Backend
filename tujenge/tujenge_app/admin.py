from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Chama, Contribution , Loan


# Register your models here.
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'role', 'is_verified', 'is_staff')
    list_filter = ('role', 'is_verified')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'role', 'chama', 'otp', 'otp_created_at')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'role', 'chama', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(User, UserAdmin)
admin.site.register(Chama)
admin.site.register(Contribution) 
admin.site.register(Loan) 


