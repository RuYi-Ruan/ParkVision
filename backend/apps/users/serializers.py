"""users 模块的序列化器。"""

from rest_framework import serializers


class UserLoginSerializer(serializers.Serializer):
    """校验登录接口所需的最小字段集。"""

    username = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(required=True, allow_blank=False, write_only=True)
