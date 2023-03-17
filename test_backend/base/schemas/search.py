import graphene
from typing import Optional
from datetime import datetime as dt
from django.db.models import JSONField, Q
from graphql import GraphQLError


class date:
    def __call__(self, date_str):
        try:
            date_obj = dt.strptime(date_str, "%d/%m/%Y").date()
            return date_obj.strftime("%Y-%m-%d %H:%M:%S.%f%z")
        except ValueError:
            raise ValueError(
                "Invalid date format. Date must be in the format DD/MM/YYYY."
            )


class time:
    def __call__(self, time_str):
        try:
            time_obj = dt.strptime(time_str, "%H:%M:%S").time()
            return time_obj.strftime("%Y-%m-%d %H:%M:%S.%f%z")
        except ValueError:
            raise ValueError(
                "Invalid time format. Time must be in the format HH:MM:SS."
            )


class DateTime:
    def __call__(self, datetime_str):
        try:
            datetime_obj = dt.strptime(datetime_str, "%d/%m/%Y %H:%M:%S")
            return datetime_obj.strftime("%Y-%m-%d %H:%M:%S.%f%z")
        except ValueError:
            raise ValueError(
                "Invalid datetime format. Datetime must be in the format DD/MM/YYYY HH:MM:SS."
            )


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

    field: Optional[graphene.Field] = None
    value = graphene.String(description="Value to filter on")
    value_type = graphene.Field(InputTypeEnum)
    operator = graphene.Field(
        SearchOperatorEnum, description="Filter operator", required=True
    )
    filters: Optional[graphene.List] = None

    @classmethod
    def input_type(cls, model_class):
        cls.model_class = model_class
        return type(
            f"{model_class.__name__}FilterTypeInput",
            (cls,),
            {
                "field": graphene.Field(
                    lambda: create_field_enum(model_class),
                    description="Field to filter on",
                ),
                "filters": graphene.List(
                    lambda: FilterTypeInput.input_type(model_class)
                ),
            },
            description=f"Input type to filter {model_class.__name__} queryset",
        )


def validate_value_n_operator(value, value_type, operator):
    string_ops = ["eq", "neq", "contains", "notContains"]

    num_date_ops = ["eq", "neq", "gt", "gte", "lt", "lte"]

    bool_ops = ["eq", "neq"]

    date_value_types = ["Date", "Time", "DateTime"]

    if not operator:
        raise GraphQLError("Operator was not provided")

    operator = operator.name

    if isinstance(value, str):
        if value_type and value_type.name in date_value_types:
            if operator in num_date_ops:
                return
        else:
            if operator in string_ops:
                return

    elif isinstance(value, bool) and operator in bool_ops:
        return

    elif (type(value) in (float, int)) and operator in num_date_ops:
        return
    
    elif value is None and operator in bool_ops:
        return

    value_type = (
        value_type.name
        if value_type and value_type.name in date_value_types
        else type(value)
    )
    msg = "Can't use operator %s with value type %s" % (operator, value_type)
    raise GraphQLError(msg)


def build_filter_criteria(model, filter_input):
    """
    Helper function to recursively build the search criteria.

    Note: when filtering by JSONField the value must be a string
    in this format: "[field]:[value]"
    """
    q = Q()

    if filter_input.filters:
        for item in filter_input.filters:
            if filter_input.operator.name == "AND":
                q &= build_filter_criteria(model, item)
            elif filter_input.operator.name == "OR":
                q |= build_filter_criteria(model, item)
    else:
        value = None
        if filter_input.value and filter_input.value_type:
            value = filter_input.value_type.value(filter_input.value)
        else:
            value = filter_input.value

        # validate match between operator and value
        validate_value_n_operator(value, filter_input.value_type, filter_input.operator)

        # check if value is null and the value was not parsed by valueType
        # then filter the items with isnull
        exact_ops_null_value = ["eq", "neq"]
        op = filter_input.operator.value
        if (
            not value
            and not filter_input.value_type
            and filter_input.operator.name in exact_ops_null_value
        ):
            op = "isnull" if filter_input.operator.name == "eq" else "not_isnull"
            value = True

        model_field = model._meta.get_field(filter_input.field.name)

        if isinstance(model_field, JSONField) and isinstance(value, str):
            json_field = value.split(":")[0]
            json_value = value.split(":")[1]

            if op.startswith("not_"):
                op = op[4:]
                q = ~Q(**{f"{filter_input.field.name}__{json_field}__{op}": json_value})
            else:
                q = Q(**{f"{filter_input.field.name}__{json_field}__{op}": json_value})
        else:
            if op.startswith("not_"):
                op = op[4:]
                q = ~Q(**{f"{filter_input.field.name}__{op}": value})
            else:
                q = Q(**{f"{filter_input.field.name}__{op}": value})

    return q
