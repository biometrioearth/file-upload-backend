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
        return value
    
    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.ObjectValueNode):
            json_dict = {}
            for field_node in node.fields:
                json_dict[field_node.name.value] = field_node.value.value
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