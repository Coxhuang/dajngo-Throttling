[TOC]

# Throttling

## #0 Blog
```
https://blog.csdn.net/Coxhuang/article/details/86690380
```

## #1 环境

```
Python3.6
Django==2.0.6
djangorestframework==3.8.2
```

## #2 需求分析
- 给客户开发一个后端接口,但是客户不是VPI会员,每天只能访问该接口10次,这时候节流就可以排上用场啦
- 用户访问登录接口,要求用户在一分钟内访问超过3次,需要输入验证码,这时候,也可以使用节流


## #3 什么是节流
限制类似于权限，因为它确定是否应该授权请求。Throttles表示临时状态，用于控制客户端可以对API发出的请求的速率。

## #4 官方提供的节流库

### #4.1 开始

#### 新建一个Django项目
#### settings.py

```
INSTALLED_APPS = [
    ...
    'rest_framework',
    'app',
]
```


```
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle', # 匿名用户节流
        'rest_framework.throttling.UserRateThrottle' # 登录用户节流
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '2/m', # 匿名用户对应的节流次数
        'user': '5/m' # 登录用户对应 的节流次数
    }
}
```

#### views.py


```
from rest_framework.throttling import UserRateThrottle
from rest_framework.throttling import AnonRateThrottle

class view(mixins.ListModelMixin,GenericViewSet):

    throttle_classes = (UserRateThrottle,)  # 登录用户节流
    serializer_class = viewSerializer
    queryset = models.UserProfile.objects.all()
    
```


```
AnonRateThrottle：用户未登录请求限速，通过IP地址判断

UserRateThrottle：用户登陆后请求限速，通过token判断
```

注意:
如果在settings.py中设置有 **UserRateThrottle / AnonRateThrottle** 那么在所有接口函数中,都默认使用AnonRateThrottle节流,即,即使在接口中没有使用节流,也默认是AnonRateThrottle节流,只有在每个接口中加上
**throttle_classes = ()** 才认为接口没有使用节流

#### #4.2 改进

为什么要自定义节流: 因为官方提供的节流,导致每一个接口都会使用,如果不使用,还需要设置为空**throttle_classes = ()**, 这样会很麻烦

settings.py

```
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': (
        # 'rest_framework.throttling.AnonRateThrottle',
        # 'rest_framework.throttling.UserRateThrottle'
        'rest_framework.throttling.ScopedRateThrottle',  # throttle_scope = 'uploads'
    ),
    'DEFAULT_THROTTLE_RATES': {
        # 'anon': '2/m',
        # 'user': '5/m'
        'uploads': '7/m',
    }
}
```

view.py

```
    throttle_scope = "uploads"
```
这样,像在哪个接口添加节流,直接添加,步添加的接口也不需要设置就留为空


### #5 自定义节流



#### #5.1 需求分析
- 登录时,密码错误三次,需要输入验证码


#### #5.2 新建文件 throttling.py

```
from __future__ import unicode_literals

from rest_framework.throttling import BaseThrottle,SimpleRateThrottle

COUNT = 0
class ScopedRateThrottle(SimpleRateThrottle):
    """
    自定义节流,节流不会限制访问,使用时,需要配合getCaptchasStatus()使用,当用户访问超出时,getCaptchasStatus返回False
    """
    scope_attr = 'throttle_no_scope'
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

```

#### #5.3 settings.py


```
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': (
        # 'rest_framework.throttling.AnonRateThrottle',
        # 'rest_framework.throttling.UserRateThrottle'
        "app.throttling.ScopedRateThrottle",  # 自定义节流  throttle_no_scope = 'uploads'
    ),
    'DEFAULT_THROTTLE_RATES': {
        # 'anon': '2/m',
        # 'user': '5/m'
        'myThrottlingChackCaptchas': '3/m',  # 限制请求验证码次数

    }
}
```









