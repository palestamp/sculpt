
class ValidationError(Exception):
    def __init__(self, message, **kwargs):
        super(ValidationError, self).__init__(message)
        self.kwargs = kwargs


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


class InSetValidator(BaseValidator):
    def __init__(self, values=None, allow_none=False, **error_kwargs):
        self.values = set(values)
        self.allow_none = allow_none
        self.error_kwargs = error_kwargs

    def validate(self, context, field):
        exists = field.has(context)
        value = field.get(context)

        if not exists and self.allow_none:
            return

        error_kwargs = {
            "label": field.label,
            "section": field.section
        }
        error_kwargs.update(self.error_kwargs)

        if not exists or value not in self.values:
            raise ValidationError("{}:{} field does not belong to requested values".format(
                field.section, field.label), **error_kwargs)
