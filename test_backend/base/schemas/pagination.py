import math
import graphene

from test_backend.base.schemas.auth import check_auth
from test_backend.base.schemas.search import build_filter_criteria
from django.db.models import Q

class PageInfoType(graphene.ObjectType):
    """
    A type for pagination info
    """

    total_count = graphene.Int()
    total_pages = graphene.Int()
    has_next_page = graphene.Boolean()
    has_prev_page = graphene.Boolean()
    page_size = graphene.Int()
    current_page = graphene.Int()


class PaginationType(graphene.ObjectType):
    """
    An abstract type for implementing pagination.
    """

    items = graphene.List(graphene.NonNull(graphene.ObjectType))
    page_info = graphene.Field(PageInfoType, required=True)

    class Meta:
        abstract = True

    @classmethod
    def resolve_items(cls, queryset, page_size, page):
        # Get the total count of items
        total_count = queryset.count()

        # Get total pages
        total_pages = math.ceil(total_count / page_size)

        if page and page_size:
            queryset = queryset[(page - 1) * page_size :]

        if page_size:
            queryset = queryset[:page_size]

        # Create the pagination info object
        page_info = PageInfoType(
            total_count=total_count,
            total_pages=total_pages,
            has_next_page=True if (page + 1) <= total_pages else False,
            has_prev_page=True if (page - 1) != 0 else False,
            page_size=page_size,
            current_page=page,
        )

        # Return the paginated results and pagination info object
        return (queryset, page_info)


class PaginatedResultType(PaginationType):
    """
    A concrete type that provides a list of paginated items.
    """

    def __init__(self, items, page_info):
        super().__init__(
            page_info=page_info,
        )
        self.items = items


def resolve_with_pagination(Model, info, search, filters, page_size, page):
    """
    A generic resolver function that applies pagination to a queryset and returns a paginated response.
    """
    # check if request is authenticated
    check_auth(info)

    # Get the queryset for the model
    queryset = Model.objects.all()

    # Apply search if specified
    if search:
        queryset = queryset.filter(search)
    
    # Apply filters if specified
    if filters:
        filter_criteria = build_filter_criteria(filters)
        print(filter_criteria)
        queryset = queryset.filter(filter_criteria)

    # Apply pagination to the queryset
    queryset, page_info = PaginationType.resolve_items(queryset, page_size, page)

    # Return the paginated results and pagination info object
    return PaginatedResultType(items=queryset, page_info=page_info)