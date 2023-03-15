import graphene

from test_backend.Authentication.models import User
from test_backend.base.schemas import (
    TestMutation,
    TestDeleteMutation
)

def save_with_password(form):
    password = form.cleaned_data.pop("password")
    instance = form.save(commit=False)
    instance.set_password(password)
    instance.save()
    return instance

# Mutations
class UserMutation(TestMutation):
    
    class Meta:
        abstract = True

    @classmethod
    def perform_mutate(cls, form, info):
        if hasattr(form, "save"):
            # override save method to set user password
            instance = save_with_password(form)

            return cls(errors=[], **instance.to_dict(fields=cls._meta.fields.keys()))
        return cls(errors=[], **form.cleaned_data)

class UserCreateMutation(UserMutation):
    """
    Creates a user with given username and password.
    """
    class Meta:
        model_class = User
        exclude_fields = (
            "is_active",
            "last_login",
            "date_joined",
            "user_permissions",
            "observation_score",
            "observation_count",
        )

class UserUpdateMutation(UserMutation):
    """
    Update user mutation.
    """
    class Meta:
        model_class = User
        mutation_create = False
        exclude_fields = (
            "last_login",
            "date_joined",
            "observation_score",
            "observation_count",
        )


class UserDeleteMutation(TestDeleteMutation):
    """
    Deletes a user with the given id.
    """
    class Meta:
        model_class = User


class Mutation(graphene.ObjectType):
    create_user = UserCreateMutation.Field()
    update_user = UserUpdateMutation.Field()
    delete_user = UserDeleteMutation.Field()
