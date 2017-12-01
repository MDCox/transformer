from transformer.registry import register
from transformer.transforms.base import BaseTransform
import re

class StringPatternExtractTransform(BaseTransform):

    category = 'string'
    name = 're_extract'
    label = 'Extract pattern'
    help_text = 'Find a pattern out of a text field. Returns all groups from the first match only.'

    noun = 'Text'
    verb = 'find a pattern from'

    def transform(self, str_input, pattern, **kwargs):
        if not str_input:
            return u''

        result = {
            '_matched': False,
        }
        
        match = re.search(re.compile(pattern), str_input)

        if not match:
            return result
            
        result.update({
            '_matched': True,
            '_start': match.start(),
            '_end': match.end(),
        })
        
        for idx, val in enumerate(match.groups()):
            result[idx] = val
        
        result.update(match.groupdict())

        return result

    def fields(self, *args, **kwargs):
        return [
            {
                'type': 'unicode',
                'required': True,
                'key': 'old',
                'label': 'Pattern',
                'help_text': 'Enter a [Python Regular Expression](https://developers.google.com/edu/python/regular-expressions) to find the first match for.'
            },
        ]


register(StringPatternExtractTransform())
