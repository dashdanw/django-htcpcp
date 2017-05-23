from django.http import HttpResponse

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


class HTCPCPMiddleware(MiddlewareMixin):
    coffee_list = [
        '/coffee/black/',
        '/coffee/espresso/'
    ]

    coffee_methods = [
        'BREW',
        'WHEN'
    ]

    def process_request(self, request):
        if request.path not in self.coffee_list and request.method not in self.coffee_methods:
            return

        if request.path not in self.coffee_list:
            return HttpResponse("I'm a teapot.", status=418)

        if request.path in self.coffee_list and request.method == 'BREW':
            return HttpResponse("Say WHEN . . . ", status=100)

        if request.path in self.coffee_list and request.method == 'WHEN':
            return HttpResponse("Mmmmmmm coffee!", status=201)
