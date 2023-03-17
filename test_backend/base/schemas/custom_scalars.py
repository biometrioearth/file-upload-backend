import json
from django.db.models import JSONField
from graphql.language import ast
from graphene.types import Scalar

class JSONObject(Scalar):
    """
    Allows use of a JSON Object for input / output from the GraphQL schema.
    """

    @staticmethod
    def serialize(value):
        def _serialize_object(obj):
            result = {}
            for key, val in obj.items():
                if isinstance(val, dict):
                    result[key] = _serialize_object(val)
                elif isinstance(val, list):
                    result[key] = _serialize_list(val)
                elif isinstance(val, (int, float)):
                    result[
                        key
                    ] = val  # Numeric values should not be enclosed in quotes
                else:
                    result[key] = val
            return result

        def _serialize_list(lst):
            result = []
            for val in lst:
                if isinstance(val, dict):
                    result.append(_serialize_object(val))
                elif isinstance(val, list):
                    result.append(_serialize_list(val))
                elif isinstance(val, (int, float)):
                    result.append(
                        val
                    )  # Numeric values should not be enclosed in quotes
                else:
                    result.append(val)
            return result

        return _serialize_object(value)

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.ObjectValueNode):
            json_dict = {}
            for field_node in node.fields:
                value_node = field_node.value
                if isinstance(value_node, ast.StringValueNode):
                    value = value_node.value
                elif isinstance(value_node, ast.IntValueNode):
                    value = int(value_node.value)
                elif isinstance(value_node, ast.FloatValueNode):
                    value = float(value_node.value)
                else:
                    raise ValueError("Invalid JSON")
                json_dict[field_node.name.value] = value
            return JSONField().to_python(json_dict)
        return None

    @staticmethod
    def parse_value(value):
        try:
            # Validate if the input is a valid JSON
            json.loads(value)
            # Parse the input if it's a valid JSON
            return JSONField().to_python(value)
        except (TypeError, ValueError):
            raise ValueError("Invalid JSON")