from rest_framework import serializers


class ParkingRecordSerializer(serializers.Serializer):
    plate_number = serializers.CharField(required=False, allow_blank=True)
    action = serializers.CharField(required=False, allow_blank=True)

