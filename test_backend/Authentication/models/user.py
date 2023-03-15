
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

from test_backend.base.models import TestBaseModel


class TestUserManager(BaseUserManager):
    """
    Creates a user manager for custom User model
    """

    def create_user(self, username, password, **extra_fields):
        """
        Create and save a User with the given username and password.
        """
        user = self.model(username=username, **extra_fields)

        user.set_password(password)

        user.save(using=self.db)

        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Create and save a SuperUser with the given username and password.
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(username, password, **extra_fields)

    def create_robot(self, username, password, **extra_fields):
        """
        Create and save a user for an AI model with the given
        username and password.
        """

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("can_login", False)

        return self.create_user(username, password, **extra_fields)


class User(AbstractUser, TestBaseModel):
    """
    Extend the Django's User Model

    Django's User model already has this fields:

        - username:     Required. 150 characters or fewer. Usernames may contain
                        alphanumeric, _, @, +, . and - characters.

        - first_name:   Optional (blank=True). 150 characters or fewer.

        - last_name:   Optional (blank=True). 150 characters or fewer.

        - email:        Optional (blank=True). Email address.

        - password:     Required. A hash of, and metadata about, the password.

        - is_active:    Boolean. Designates whether this user account should be
                        considered active.

        - is_staff:     Boolean. Designates whether this user can access the admin
                        site.

        - is_superuser: Boolean. Designates that this user has all permissions
                        without explicitly assigning them.

        - last_login:   A datetime of the user's last login.

        - date_joined:  A datetime designating when the account was created. Is set
                        to the current date/time by default when the account is
                        created.

        - groups:       Many-to-many relationship to Group.

        - user_permissions: Many-to-many relationship to Permission.
    """

    can_login = models.BooleanField(
        verbose_name="Can login?",
        help_text="Indicates if user is a person and can login, or an AI model",
        blank=False,
        null=False,
        default=True,
    )

    # disable created_at from TestBaseModel to use date_joined from AbstractUser
    created_at = None

    def __str__(self):
        return str(self.username)

    objects = TestUserManager()

    class Meta:
        db_table = "Users"

        verbose_name = "User"

        verbose_name_plural = "Users"

        unique_together = [
            [
                "username",
            ],
        ]
