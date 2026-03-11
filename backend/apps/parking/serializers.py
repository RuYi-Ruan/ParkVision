from rest_framework import serializers


class ParkingSpaceSerializer(serializers.Serializer):
    space_code = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)

