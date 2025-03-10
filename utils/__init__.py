import sys
import logging

logger = logging.getLogger(__file__)

def lazy_discover_foreign_id_choices(model, **kwargs):
    if ('makemigrations' in sys.argv or 'migrate' in sys.argv):
        return []
    try:
        if kwargs:
            return model.objects.filter(**kwargs)
        return model.objects.all()
    except Exception as exp:
        logger.error("Exception occured: %s\nmodel: %s\n_filter:'%s'",exp, model, kwargs)
    return []

