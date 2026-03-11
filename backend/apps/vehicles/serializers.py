from rest_framework import serializers


class VehicleSerializer(serializers.Serializer):
    plate_number = serializers.CharField(required=False, allow_blank=True)
    owner_name = serializers.CharField(required=False, allow_blank=True)

