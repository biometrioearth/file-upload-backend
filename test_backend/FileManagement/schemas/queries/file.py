import os
import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q

from test_backend.FileManagement.models import File

from test_backend.base.schemas.custom_scalars import JSONObject
from test_backend.base.schemas import (
    resolve_with_pagination,
    check_auth,
    PageInfoType,
    FilterTypeInput,
)


class FileType(DjangoObjectType):
    """
    Default type for Files.
    """
    file_metadata = JSONObject()

    file = graphene.String()

    class Meta:
        model = File
        fields = "__all__"

    def resolve_file(self, info):
        return "http://localhost:" + os.environ.get("TEST_APP_PORT", "7070") + self.file.url
        


class PaginatedFileType(graphene.ObjectType):
    """
    A type to return a paginated result for Files.
    """

    page_info = graphene.Field(PageInfoType)
    items = graphene.List(FileType)


class Query(graphene.ObjectType):
    # Set the model attribute on the FilterTypeInput class
    FileFilterTypeInput = FilterTypeInput.input_type(File)

    file = graphene.Field(
        FileType,
        id=graphene.ID(),
        name=graphene.String(),
    )

    all_files = graphene.Field(
        PaginatedFileType,
        search=graphene.String(),
        filters=graphene.Argument(FileFilterTypeInput),
        page_size=graphene.Int(),
        page=graphene.Int(),
    )

    def resolve_file(self, info, id=None, name=None):
        check_auth(info)

        if id:
            return File.objects.get(pk=id)
        
        if name:
            return File.objects.get(name=name)


    def resolve_all_files(self, info, search=None, filters=None, page_size=10, page=1):
        return resolve_with_pagination(
            File,
            info,
            (Q(name__icontains=search) | Q(url__icontains=search))
            if search
            else None,
            filters,
            page_size,
            page,
        )