from django.template.defaultfilters import register


@register.filter(name='dict_key')
def dict_key(dict_data, key):
    """
    usage example {{ your_dict|get_value_from_dict:your_key }}
    """
    if key:
        return dict_data.get(key, None)
