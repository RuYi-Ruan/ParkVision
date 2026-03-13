"""系统设置模块的序列化器。"""

from rest_framework import serializers


class ParkingRuleSerializer(serializers.Serializer):
    """停车收费与运营规则配置。"""

    free_minutes = serializers.IntegerField(min_value=0, max_value=240)
    fee_per_hour = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=0)
    daily_cap = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=0)
    overdue_hours = serializers.IntegerField(min_value=1, max_value=168)


class RecognitionConfigSerializer(serializers.Serializer):
    """识别服务相关配置。"""

    detect_confidence = serializers.DecimalField(max_digits=4, decimal_places=2, min_value=0, max_value=1)
    ocr_confidence = serializers.DecimalField(max_digits=4, decimal_places=2, min_value=0, max_value=1)
    yolo_model_path = serializers.CharField(max_length=255)
    plate_model_path = serializers.CharField(max_length=255)


class RuntimeConfigSerializer(serializers.Serializer):
    """系统运行时的展示和刷新配置。"""

    default_zone = serializers.CharField(max_length=50)
    monitor_refresh_seconds = serializers.IntegerField(min_value=5, max_value=300)
    auto_export_days = serializers.IntegerField(min_value=1, max_value=365)
    retain_days = serializers.IntegerField(min_value=1, max_value=3650)


class SystemConfigSerializer(serializers.Serializer):
    """系统设置整体配置结构。"""

    parking_rule = ParkingRuleSerializer()
    recognition = RecognitionConfigSerializer()
    runtime = RuntimeConfigSerializer()
