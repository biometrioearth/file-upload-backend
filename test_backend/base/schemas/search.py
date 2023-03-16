import graphene
from typing import Optional
from django.db.models import Q
from datetime import datetime as dt

class date:

    def __call__(self, date_str):
        try:
            date_obj = dt.strptime(date_str, '%d/%m/%Y').date()
            return date_obj.strftime("%Y-%m-%d %H:%M:%S.%f%z")
        except ValueError:
            raise ValueError('Invalid date format. Date must be in the format DD/MM/YYYY.')


class time:

    def __call__(self, time_str):
        try:
            time_obj = dt.strptime(time_str, '%H:%M:%S').time()
            return time_obj.strftime("%Y-%m-%d %H:%M:%S.%f%z")
        except ValueError:
            raise ValueError('Invalid time format. Time must be in the format HH:MM:SS.')
        

class DateTime:

    def __call__(self, datetime_str):
        try:
            datetime_obj = dt.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
            return datetime_obj.strftime("%Y-%m-%d %H:%M:%S.%f%z")
        except ValueError:
            raise ValueError('Invalid datetime format. Datetime must be in the format DD/MM/YYYY HH:MM:SS.')


class InputTypeEnum(graphene.Enum):
    """
    Supported input value types
    """
    Int = int
    Float = float
    String = str
    Boolean = bool

    Date = date()
    Time = time()
    DateTime = DateTime()



class SearchOperatorEnum(graphene.Enum):
    """
    Supported search operators.
    """
    eq = "exact"
    neq = "not_exact"
    gt = "gt"
    gte = "gte"
    lt = "lt"
    lte = "lte"
    contains = "icontains"
    notContains = "not_icontains"
    OR = "or"
    AND = "and"



def create_field_enum(model):
    """
    Dinamycally creates enum for fields in a model.
    """
    field_enum_values = {field.name.lower(): field.name for field in model._meta.fields}
    FieldEnum = graphene.Enum(model.__name__ + "FieldEnum", field_enum_values)


    return FieldEnum


class FilterTypeInput(graphene.InputObjectType):
    """
    An generic input type to filter querysets.
    """

    field:  Optional[graphene.Field] = None
    value = graphene.String(description="Value to filter on")
    value_type = graphene.Field(InputTypeEnum)
    operator = graphene.Field(SearchOperatorEnum,default_value=SearchOperatorEnum.contains, description="Filter operator")
    filters: Optional[graphene.List] = None


    @classmethod
    def input_type(cls, model_class):
        cls.model_class = model_class
        return type(
            f"{model_class.__name__}FilterTypeInput",
            (cls,),
            {"field": graphene.Field(
                lambda: create_field_enum(model_class),
                description="Field to filter on",
            ),
             "filters": graphene.List(lambda: FilterTypeInput.input_type(model_class)),
            },
            description=f"Input type to filter {model_class.__name__} queryset",
        )




def build_filter_criteria(filter_input):
    """
    Helper function to recursively build the search criteria.
    """
    q = Q()

    if filter_input.filters:
        for item in filter_input.filters:
            if filter_input.operator.name == 'AND':
                q &= build_filter_criteria(item)
            elif filter_input.operator.name == 'OR':
                q |= build_filter_criteria(item)
    else:

        value = None
        if filter_input.value and filter_input.value_type:
            value = filter_input.value_type.value(filter_input.value)
        else:
            value = filter_input.value

        exact_ops_null_value = ['eq','neq']

        op = filter_input.operator.value
        if not value and filter_input.operator.name in exact_ops_null_value:
            op = 'isnull' if filter_input.operator.name == 'eq' else 'not_isnull'
            value = True

        if op.startswith('not_'):
            op = op[4:]
            q = ~Q(**{f"{filter_input.field.name}__{op}": value})
        else:
            q = Q(**{f"{filter_input.field.name}__{op}": value})

    return q





