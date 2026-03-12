"""vehicles 模块的序列化器。"""

from rest_framework import serializers


class VehicleQuerySerializer(serializers.Serializer):
    """校验车辆列表接口的筛选参数。"""

    keyword = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)


class VehicleWriteSerializer(serializers.Serializer):
    """校验车辆新增和编辑时需要的字段。"""

    plate_number = serializers.CharField(required=True, allow_blank=False, max_length=20)
    owner_name = serializers.CharField(required=True, allow_blank=False, max_length=50)
    owner_phone = serializers.CharField(required=False, allow_blank=True, max_length=20)
    vehicle_type = serializers.CharField(required=True, allow_blank=False, max_length=20)
    color = serializers.CharField(required=False, allow_blank=True, max_length=20)
    status = serializers.IntegerField(required=True, min_value=0, max_value=1)
    remark = serializers.CharField(required=False, allow_blank=True, max_length=255)
