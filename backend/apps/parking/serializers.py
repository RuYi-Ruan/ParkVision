"""parking 模块的序列化器。"""

from rest_framework import serializers


class ParkingSpaceQuerySerializer(serializers.Serializer):
    """校验车位列表接口中的可选过滤参数。"""

    keyword = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)


class ParkingSpaceWriteSerializer(serializers.Serializer):
    """校验车位新增和编辑时需要的字段。"""

    space_code = serializers.CharField(required=True, allow_blank=False, max_length=20)
    area_code = serializers.CharField(required=True, allow_blank=False, max_length=20)
    space_type = serializers.CharField(required=True, allow_blank=False, max_length=20)
    status = serializers.CharField(required=True, allow_blank=False, max_length=20)
    floor_no = serializers.CharField(required=False, allow_blank=True, max_length=20)
    remark = serializers.CharField(required=False, allow_blank=True, max_length=255)
