"""detection 模块的序列化器。"""

from rest_framework import serializers


class DetectionRequestSerializer(serializers.Serializer):
    """校验识别测试接口需要的上传参数。"""

    image = serializers.ImageField(required=False)
    preset_id = serializers.CharField(required=False, allow_blank=True)
