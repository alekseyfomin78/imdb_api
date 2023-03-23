from django.core.cache import cache
from django.conf import settings


def delete_cache(key_prefix: str):
    """
    Удаление ключей из кэша по заданному key_prefix
    """
    keys_pattern = f"views.decorators.cache.cache_*.{key_prefix}.*.{settings.LANGUAGE_CODE}.{settings.TIME_ZONE}"
    cache.delete_pattern(keys_pattern)
