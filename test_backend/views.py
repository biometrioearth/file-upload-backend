from django.contrib.auth.mixins import LoginRequiredMixin
from graphene_file_upload.django import FileUploadGraphQLView


class PrivateGraphQLView(LoginRequiredMixin, FileUploadGraphQLView):
    pass