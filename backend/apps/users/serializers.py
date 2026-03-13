"""用户模块的序列化器。"""

from rest_framework import serializers


class UserLoginSerializer(serializers.Serializer):
    """校验登录接口所需的最小字段集。"""

    username = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(required=True, allow_blank=False, write_only=True)


class UserQuerySerializer(serializers.Serializer):
    """校验用户管理列表的筛选参数。"""

    keyword = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    role = serializers.CharField(required=False, allow_blank=True)


class UserWriteSerializer(serializers.Serializer):
    """校验用户新增和编辑时所需的字段。"""

    username = serializers.CharField(required=True, allow_blank=False, max_length=50)
    password = serializers.CharField(required=True, allow_blank=False, max_length=255)
    real_name = serializers.CharField(required=True, allow_blank=False, max_length=50)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    role = serializers.ChoiceField(choices=["admin", "operator", "viewer"])
    status = serializers.IntegerField(required=True, min_value=0, max_value=1)
