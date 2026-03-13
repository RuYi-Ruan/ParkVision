"""停车记录模块的序列化器。"""

from rest_framework import serializers


class RecordEntrySerializer(serializers.Serializer):
    """校验模拟入场接口所需字段。"""

    plate_number = serializers.CharField(required=True, allow_blank=False, max_length=20)
    entry_gate = serializers.CharField(required=True, allow_blank=False, max_length=50)
    space_id = serializers.IntegerField(required=False, min_value=1)
    remark = serializers.CharField(required=False, allow_blank=True, max_length=255)


class RecordExitSerializer(serializers.Serializer):
    """校验模拟出场接口所需字段。"""

    plate_number = serializers.CharField(required=True, allow_blank=False, max_length=20)
    exit_gate = serializers.CharField(required=True, allow_blank=False, max_length=50)
    remark = serializers.CharField(required=False, allow_blank=True, max_length=255)
