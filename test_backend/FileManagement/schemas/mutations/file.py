import graphene


from test_backend.FileManagement.models import File
from test_backend.base.schemas import (
    TestMutation,
    TestDeleteMutation
)



class FileCreateMutation(TestMutation):
    """
    Creates a file with given arguments.
    """
    class Meta:
        model_class = File


class FileUpdateMutation(TestMutation):
    """
    Update file mutation.
    """
    class Meta:
        model_class = File
        mutation_create = False


class FileDeleteMutation(TestDeleteMutation):
    """
    Deletes a user with the given id.
    """
    class Meta:
        model_class = File


class Mutation(graphene.ObjectType):
    create_file = FileCreateMutation.Field()
    update_file = FileUpdateMutation.Field()
    delete_file = FileDeleteMutation.Field()