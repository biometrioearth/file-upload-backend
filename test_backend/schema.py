import graphene
import graphql_jwt

from test_backend.base.schemas.graphene_gis.gis_converter import *

from test_backend.Authentication.schemas import AuthQuery, AuthMutation
from test_backend.FileManagement.schemas import FileManagementQuery, FileManagementMutation


class Query(
    AuthQuery,
    FileManagementQuery,
    graphene.ObjectType
):
    pass


class Mutation(
    AuthMutation,
    FileManagementMutation,
    graphene.ObjectType
):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
