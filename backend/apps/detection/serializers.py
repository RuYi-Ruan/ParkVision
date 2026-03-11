from rest_framework import serializers


class DetectionRequestSerializer(serializers.Serializer):
    image = serializers.ImageField(required=False)

