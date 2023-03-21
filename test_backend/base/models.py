import uuid

from django.db import models


class TestBaseModel(models.Model):
    # fields common to all models
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    updated_at = models.DateTimeField(
        verbose_name="created on", editable=False, auto_now=True
    )

    created_at = models.DateTimeField(
        verbose_name="modified on", editable=False, auto_now_add=True
    )

    class Meta:
        abstract = True

    def to_dict(self, fields=None, exclude=None):
        """
        Convert the model instance to a dictionary.
        """
        opts = self._meta
        data = {}
        for f in opts.concrete_fields:
            if exclude and f.name in exclude:
                continue

            if fields and f.name not in fields:
                continue
            
            if f.is_relation and f.many_to_one:
                data[f.name] = getattr(self, f.name)
            else:
                data[f.name] = f.value_from_object(self)
        for f in opts.many_to_many:
            if exclude and f.name in exclude:
                continue

            if fields and f.name not in fields:
                continue
            
            data[f.name] = [obj.pk for obj in getattr(self, f.name).all()]
        return data
