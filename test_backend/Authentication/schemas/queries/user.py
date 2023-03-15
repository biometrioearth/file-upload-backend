import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q

from test_backend.Authentication.models import User
from test_backend.base.schemas import (
    resolve_with_pagination,
    check_auth,
    PageInfoType,
    FilterTypeInput,
)

class UserType(DjangoObjectType):
    """
    Default type for Users, excluding password
    """

    class Meta:
        model = User

        exclude = ("password",)


class PaginatedUsersType(graphene.ObjectType):
    """
    A type to return a paginated result for Users
    """

    page_info = graphene.Field(PageInfoType)
    items = graphene.List(UserType)


class Query(graphene.ObjectType):
    # Set the model attribute on the FilterTypeInput class
    UserFilterTypeInput = FilterTypeInput.input_type(User)

    user = graphene.Field(
        UserType,
        id=graphene.ID(),
        username=graphene.String(),
    )

    all_users = graphene.Field(
        PaginatedUsersType,
        search=graphene.String(),
        filters=graphene.Argument(UserFilterTypeInput),
        page_size=graphene.Int(),
        page=graphene.Int(),
    )

    def resolve_user(self, info, id=None, username=None):
        check_auth(info)

        if id:
            return User.objects.get(pk=id)

        if username:
            return User.objects.get(username=username)

    def resolve_all_users(self, info, search=None, filters=None, page_size=10, page=1):
        return resolve_with_pagination(
            User,
            info,
            (Q(username__icontains=search) | Q(last_name__icontains=search))
            if search
            else None,
            filters,
            page_size,
            page,
        )