from transformer.util import APIError

class BaseTransform:
    category = ''
    name = ''
    label = ''
    help_text = ''

    @property
    def key(self):
        return '{}.{}'.format(self.category, self.name)

    def to_dict(self):
        return {
            'key': self.key,
            'label': self.label,
            'name': self.name,
            'category': self.category,
            'help_text': self.help_text,
            'type': 'transform'
        }

    def transform(self, *args, **kwargs):
        self.raise_exception('Must implement transform method')

    def raise_exception(self, message, status=400):
        raise APIError(message, status)

    def fields(self, *args, **kwargs):
        return []

    def _fields_internal(self, *args, **kwargs):
        return [
            {
                'type': 'unicode',
                'list': True,
                'required': True,
                'key': 'inputs',
                'help_text': 'Value(s) you would like to transform'
            }
        ] + self.fields(*args, **kwargs)
