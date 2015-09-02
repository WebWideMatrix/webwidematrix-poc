from mies.constants import INTERACTION_RATE_PERIOD
from mies.redis_config import get_cache


class InteractionBehavior:

    def _build_interactions_log_key(self):
        key = "{}_interactions".format(self._id)
        return key

    def log_interaction(self, resident_id, address):
        key = self._build_interactions_log_key()
        cache = get_cache()
        cache.hset(key, resident_id, address)
        cache.expire(key, INTERACTION_RATE_PERIOD)

    def reset_interactions_log(self):
        key = self._build_interactions_log_key()
        cache = get_cache()
        cache.delete(key)

    def get_interactions_rate(self):
        key = self._build_interactions_log_key()
        cache = get_cache()
        return cache.scard(key)
