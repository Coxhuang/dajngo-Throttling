from __future__ import unicode_literals

from rest_framework.throttling import BaseThrottle,SimpleRateThrottle

COUNT = 0
class ScopedRateThrottle(SimpleRateThrottle):
    """
    自定义节流,节流不会限制访问,使用时,需要配合getCaptchasStatus()使用,当用户访问超出时,getCaptchasStatus返回False
    """
    scope_attr = 'throttle_no_scope' # 接口使用 throttle_no_scope
    def __init__(self):
        pass

    def allow_request(self, request, view):
        global COUNT
        self.scope = getattr(view, self.scope_attr, None)
        if not self.scope:
            return True
        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)
        ret = super(ScopedRateThrottle, self).allow_request(request, view)
        if not ret:
            COUNT = 1
        else:
            COUNT = 0
        return True

    def get_cache_key(self, request, view):
        """
        If `view.throttle_scope` is not setmail, don't apply this throttle.

        Otherwise generate the unique cache key by concatenating the user id
        with the '.throttle_scope` property of the view.
        """
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


def getCaptchasStatus():
    if COUNT == 1:
        return True
    else:
        return False
