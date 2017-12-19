

class ValidationError(Exception):
    def __init__(self, message, **kwargs):
        super(ValidationError, self).__init__(message)
        self.kwargs = kwargs


class Validate(object):
    def __init__(self, field, validator):
        self.field = field
        self.validator = validator

    def run(self, context):
        try:
            self.validator._validate(context, self.field)  # pylint: disable=W0212
        except ValidationError as exc:
            context.errors.append(exc)


class BaseValidator(object):
    def _validate(self, context, field):
        self.validate(context, field)

    def validate(self, context, field):
        raise NotImplementedError


class NotEmptyValidator(BaseValidator):
    def __init__(self, **error_kwargs):
        self.error_kwargs = error_kwargs

    def validate(self, context, field):
        exists = field.has(context)
        if exists is False:
            error_kwargs = {
                "label": field.label,
                "section": field.section
            }
            error_kwargs.update(self.error_kwargs)
            raise ValidationError(
                message="{}:{} field does not exists".format(
                    field.section, field.label), **error_kwargs)
