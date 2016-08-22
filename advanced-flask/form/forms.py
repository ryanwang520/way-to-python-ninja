import functools
import types

from flask.globals import _app_ctx_stack, request, _app_ctx_err_msg
from werkzeug.local import LocalProxy


_none_value = object()


def _lookup_current_form():
    top = _app_ctx_stack.top
    if top is None:
        raise RuntimeError(_app_ctx_err_msg)
    return getattr(top, 'form', None)


form = LocalProxy(_lookup_current_form)

class ValidationError(Exception):
    pass


class FormField:
    VALID_SOURCES = ('args', 'form', 'json')

    def __init__(self, source='', *, name='', required=True,
                 default=None, description=''):
        if source and source not in self.VALID_SOURCES:
            raise ValueError('request source %s is not valid' % source)
        self.source = source or 'json'
        self.required = required
        self.default = default
        self.description = description
        self.name = name

    def __set__(self, instance, value):
        raise ValueError('form field attribute is readonly')

    def _get_request_data(self):
        if not hasattr(request, self.source):
            raise ValidationError(
                '%s is not a valid data source from request' % self.source)
        if self.source == 'json' and request.get_json(silent=True) is None:
            source = 'form'
        else:
            source = self.source
        req_data = getattr(request, source)
        # request.args or request.form
        if hasattr(req_data, 'getlist'):
            raw = req_data.getlist(self.name)
            if len(raw) == 1:
                return raw[0]
            if len(raw) == 0:
                return _none_value
            # 不支持多个值的表单字段, 请用csv代理
            raise ValidationError(
                'multi values form field %s is not to be supported!' % self.name)
        # request.json
        return req_data.get(self.name, _none_value)

    def __get__(self, instance, _):
        if instance is None:
            return self
        name = self.name
        data = self._get_request_data()

        if data in( _none_value, ''):
            if self.required:
                raise ValidationError('FIELD %s is required' % name)
            # return default directly
            self.__dict__[name] = self.default
            return self.default

        result = self.process(data)
        self.__dict__[name] = result
        return result

    def process(self, data):
        return data


class LengthLimitedField(FormField):
    def __init__(self, source='', *, min_length=None, max_length=None, **kwargs):
        self.min = min_length
        self.max = max_length
        super().__init__(source, **kwargs)

    def process(self, data):
        if self.max is not None and len(data) > self.max:
            raise ValidationError(
                'FIELD {} is limited to max length {} but actually is {}'.format(  # noqa
                    self.name, self.max, len(data)))
        if self.min is not None and len(data) < self.min:
            raise ValidationError(
                'FIELD {} is limited to min length {} but actually is {}'.format(  # noqa
                    self.name, self.min, len(data)))

        return super().process(data)


class SizedField(FormField):
    def __init__(self, source='', *, min_val=None, max_val=None,
                 inc_min=True, inc_max=True, **kwargs):
        self.min = min_val
        self.max = max_val
        self.inc_min = inc_min
        self.inc_max = inc_max
        super().__init__(source, **kwargs)

    def process(self, data):
        if self.max is not None:
            invalid = data > self.max if self.inc_max else data >= self.max
            if invalid:
                raise ValidationError(
                    'FIELD {} is limited to max value {} but actually is {}'.format(
                        self.name, self.max, data))
        if self.min is not None:
            invalid = data < self.min if self.inc_min else data <= self.min
            if invalid:
                raise ValidationError(
                    'FIELD {} is limited to min value {} but actually is {}'.format(
                        self.name, self.min, data))
        return super().process(data)


class TypedField(FormField):
    field_type = type(None)

    def process(self, data):
        try:
            data = self.field_type(data)
            return super().process(data)
        except (TypeError, ValueError):
            raise ValidationError(
                'FIELD {} cannot be converted to {}'.format(
                    self.name, self.field_type
                )
            )


class IntField(TypedField, SizedField):
    field_type = int


class FloatField(TypedField, SizedField):
    field_type = float


class BasicStringField(TypedField):
    field_type = str


class BoolField(TypedField):
    type = bool


class StringField(BasicStringField, LengthLimitedField):
    pass


class CSVListField(FormField):
    def __init__(self, source='', *, each_field, **kwargs):
        self.each_field = each_field
        super().__init__(source, **kwargs)

    def process(self, data):
        data_list = data.split(',')
        if isinstance(self.each_field, FormField):
            each_field = self.each_field
        else:
            each_field = self.each_field(source=self.source)
        return [each_field.process(elem) for elem in data_list]


class FormFieldMeta(type):
    def __new__(cls, name, bases, attrs):
        for field, value in attrs.items():
            if isinstance(value, FormField):
                value.name = field
        return type.__new__(cls, name, bases, attrs)


class Form(metaclass=FormFieldMeta):
    def __init__(self, view_func):
        self._view_func = view_func
        functools.update_wrapper(self, view_func)

    def __call__(self, *args, **kwargs):
        # lazy load form data when accessing
        _app_ctx_stack.top.form = self
        return self._view_func(*args, **kwargs)

    def __get__(self, instance, _):
        if instance is None:
            return self
        return types.MethodType(self, instance)
