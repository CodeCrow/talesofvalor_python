from django import template


register = template.Library()


# https://stackoverflow.com/a/24658162/2689986
@register.simple_tag
def add_query_params(request, **kwargs):
    """
    Takes a request and generates URL with given kwargs as query parameters
    e.g.
    1. {% add_query_params request key=value %} with request.path=='/ask/'
        => '/ask/?key=value'
    2. {% add_query_params request page=2 %} with request.path=='/ask/?key=val'
        => '/ask/?key=value&page=2'
    3. {% add_query_params request page=5 %} with request.path=='/ask/?page=2'
        => '/ask/?page=5'
    """
    updated = request.GET.copy()
    for k, v in kwargs.items():
        updated[k] = v

    return request.build_absolute_uri('?'+updated.urlencode())
