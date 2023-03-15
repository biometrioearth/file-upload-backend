from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


class UserAdmin(BaseUserAdmin):
    model = User

    BaseUserAdmin.fieldsets += (
        (
            "User's observations",
            {
                "fields": (
                    (
                        "can_login",
                    ),
                )
            },
        ),
    )


admin.site.register(User, UserAdmin)

