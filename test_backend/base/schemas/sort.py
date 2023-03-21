import graphene
from typing import Optional

from test_backend.base.schemas.search import create_field_enum


class SortInputTypeEnum(graphene.Enum):
    """
    Supported input value types
    """

    DESC = "desc"
    ASC = "asc"


class SortTypeInput(graphene.InputObjectType):
    """
    An generic input type to filter querysets.
    """

    field: Optional[graphene.Field] = None
    order = graphene.Field(SortInputTypeEnum)

    @classmethod
    def input_type(cls, model_class):
        cls.model_class = model_class
        return type(
            f"{model_class.__name__}SortTypeInput",
            (cls,),
            {
                "field": graphene.Field(
                    lambda: create_field_enum(model_class),
                    description="Field to sort with",
                )
            },
            description=f"Input type to sort {model_class.__name__} queryset",
        )


def sort_queryset(qs, sort):
    """
    Helper function to sort queryset by sort items in sort list.
    """

    sort_params = []
    for sort_item in sort:
        if sort_item.order.name == "DESC":
            sort_params.append("-" + sort_item.field.name)
        else:
            sort_params.append(sort_item.field.name)

    return qs.order_by(*sort_params)
