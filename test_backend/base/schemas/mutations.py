import re
from collections import OrderedDict
from django.db.models import ForeignKey, OneToOneField, ManyToManyField, JSONField, FileField
from django.db.models.fields import Field
from django.forms import modelform_factory

from graphene import Field, InputField, ID, Mutation, Argument, NonNull, List, String
from graphene.relay.mutation import maybe_thenable
from graphene.types.mutation import MutationOptions
from graphene.types.dynamic import Dynamic
from graphene_file_upload.scalars import Upload

from graphene_django.converter import convert_django_field
from graphene_django.forms.mutation import (
    yank_fields_from_attrs,
    ErrorType,
    _set_errors_flag_to_context,
    get_global_registry,
)

from test_backend.base.schemas.auth import check_auth
from test_backend.base.schemas.custom_scalars import JSONObject


def return_graphene_type(field, input, registry=None):

    if isinstance(field,JSONField):
        return JSONObject()
    
    if isinstance(field,FileField) and input:
        return Upload()

    if not input:
        field.null = True
        return convert_django_field(field,registry)

    else:
        if isinstance(field,ForeignKey) or isinstance(field,OneToOneField):
            return ID()
        elif isinstance(field,ManyToManyField):
            return List(ID)
        else:
            return convert_django_field(field,registry)


def fields_from_model(model, only_fields, exclude_fields, input=True):
    # Get all fields of the User model
    model_fields = model._meta.fields

    fields = OrderedDict()

    # exclude updated_at and created_at default fields and also password
    exclude_fields = exclude_fields + ('updated_at','created_at',)
    for model_field in model_fields:
        is_not_in_only = only_fields and model_field.name not in only_fields
        is_excluded = (
            model_field.name
            in exclude_fields
        )

        if is_not_in_only or is_excluded:
            continue
    
        registry = get_global_registry()

        fields[model_field.name] = return_graphene_type(model_field,input,registry)

    return fields


def create_dynamic_form(model, data):
    # Create a dynamic form class using modelform_factory
    DynamicForm = modelform_factory(model, fields=list(data.keys()))

    # Override form fields labels with the input data keys
    for key, value in data.items():
        DynamicForm.base_fields[key].label = key

    return DynamicForm


class TestMutationOptions(MutationOptions):
    model_class = None

class BaseMutation(Mutation):
    """
    Base mutation class for test, it's basically ClientIDMutation
    from graphene.relay but modified to our needs.
    """

    class Meta:
        abstract = True

    errors = List(ErrorType)

    @classmethod
    def __init_subclass_with_meta__(
        cls, output=None, input_fields=None, arguments=None, name=None, model_class=None, **options
    ):
        base_name = re.sub("Payload$", "", name or cls.__name__)

        assert not output, "Can't specify any output"
        assert not arguments, "Can't specify any arguments"
        
        cls.model_class = model_class

        if not input_fields:
            input_fields = {}

        arguments = dict()

        for field_name, input_field in input_fields.items():
            model_field = cls.model_class._meta.get_field(field_name)
            is_required = True if not model_field.blank and not model_field.null else False
            argument_type = (
                input_field.type.of_type
                if isinstance(input_field.type, NonNull)
                else input_field.type
            )
            argument = Argument(
                argument_type,
                required=(
                    is_required
                    if 'id' not in input_fields 
                    or field_name == 'id'
                    else False
                ),
                description=input_field.description if not isinstance(input_field, Dynamic) else "",
                default_value=input_field.default_value if not isinstance(input_field, Dynamic) else None,
            )
            arguments[field_name] = argument

        mutate_and_get_payload = getattr(cls, "mutate_and_get_payload", None)
        if cls.mutate and cls.mutate.__func__ == BaseMutation.mutate.__func__:
            assert mutate_and_get_payload, (
                f"{name or cls.__name__}.mutate_and_get_payload method is required"
                " in a TestMutation."
            )

        if not name:
            name = f"{base_name}Payload"

        super().__init_subclass_with_meta__(
            output=None, arguments=arguments, name=name, model_class=model_class, **options
        )

    @classmethod
    def mutate(cls, root, info, **input):
        # check if request is authenticated
        check_auth(info)

        def on_resolve(payload):
            return payload

        result = cls.mutate_and_get_payload(root, info, **input)
        return maybe_thenable(result, on_resolve)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        form = cls.get_form(root, info, **input)

        if form.is_valid():
            return cls.perform_mutate(form, info)
        else:
            errors = ErrorType.from_errors(form.errors)
            _set_errors_flag_to_context(info)

            data = {}
            if 'id' in input:
                instance = cls.model_class._default_manager.get(pk=input['id'])
                data = instance.to_dict(fields=cls._meta.fields.keys())
            
            return cls(errors=errors, **data)

    @classmethod
    def get_form(cls, root, info, **input):
        id_field = input.pop('id',None)
        form_class = create_dynamic_form(cls.model_class, input)
        input.update({'id': id_field})
        form_kwargs = cls.get_form_kwargs(root, info, **input)
        if "file_data" in form_kwargs:
            form = form_class(
                form_kwargs["data"],
                form_kwargs["file_data"], 
                instance=form_kwargs["instance"] if "instance" in form_kwargs else None
            )
        else:
            form = form_class(
                form_kwargs["data"],
                instance=form_kwargs["instance"] if "instance" in form_kwargs else None
            )

        return form

    @classmethod
    def get_form_kwargs(cls, root, info, **input):
        kwargs = {"data": input}

        pk = input.pop("id", None)
        if pk:
            instance = cls.model_class._default_manager.get(pk=pk)
            kwargs["instance"] = instance

        file_data = {}
        for field in cls.model_class._meta.fields:
            if isinstance(field, FileField) and field.name in kwargs["data"].keys():
                file_data[field.name] = kwargs["data"][field.name]

        if len(file_data.keys()) > 0:
            kwargs["file_data"] = file_data

        return kwargs

    @classmethod
    def perform_mutate(cls, form, info):
        if hasattr(form, "save"):
            # `save` method won't exist on plain Django forms, but this mutation can
            # in theory be used with `ModelForm`s as well and we do want to save them.
            instance = form.save()

            return cls(errors=[], **instance.to_dict(fields=cls._meta.fields.keys()))
        return cls(errors=[], **form.cleaned_data)


class TestMutation(BaseMutation):
    """
    Base update mutation class for test. Adds id field as required
    in the input arguments.
    """

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
        cls, model_class=None, only_fields=(), exclude_fields=(), mutation_create=True ,**options
    ):

        if not model_class:
            raise Exception("model_class is required for TestMutation")
        
        
        if not mutation_create and len(only_fields) > 0:
            only_fields = ('id',) + only_fields

        input_fields = fields_from_model(model_class, only_fields, exclude_fields)

        if mutation_create:
            # exclude id in the input fields for create mutations
            input_fields.pop('id',None)

        output_fields = fields_from_model(model_class, (), ('password',),False)

        _meta = TestMutationOptions(cls)
        _meta.fields = yank_fields_from_attrs(output_fields, _as=Field)

        input_fields = yank_fields_from_attrs(input_fields, _as=InputField)
        super().__init_subclass_with_meta__(
            _meta=_meta, input_fields=input_fields, model_class=model_class, **options
        )



class TestDeleteMutation(BaseMutation):
    """
    Base delete mutation class for test.
    """

    id = ID()
    message = String()

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, model_class=None, **options):

        if not model_class:
            raise Exception("model_class is required for TestMutation")
        
        input_fields = {"id": ID(required=True)}

        input_fields = yank_fields_from_attrs(input_fields, _as=InputField)
        super().__init_subclass_with_meta__(
            input_fields=input_fields, model_class=model_class, **options
        )

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        id = input["id"]
        cls.get_queryset(cls.model_class.objects.all(), info).get(id=id).delete()
        return cls(id=id, message=f"{cls.model_class.__name__} deleted")
