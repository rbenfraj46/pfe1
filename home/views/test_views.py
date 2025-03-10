
from home.views.index import IndexView
from django.contrib import messages

from django.utils.translation import gettext_lazy as _


class TestView(IndexView):
    template_name =  "test.html"

    def get(self, request, *args, **kwargs):
        messages.success(request, _('Your subscription is activated successfully.'))
        messages.info(request, _('Your subscription is activated successfully.'))
        messages.error(request, _('Your subscription is activated successfully.'))
        messages.warning(request, _('Your subscription is activated successfully.'))
        return super().get(request, *args, **kwargs)
