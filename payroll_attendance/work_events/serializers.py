from rest_framework import serializers

from .models import SickLeave, Leave, Permission


class SickLeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = SickLeave
        fields = "__all__"
        read_only_fields = ["created_at"]


class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = "__all__"
        read_only_fields = ["created_at"]


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"
        read_only_fields = ["created_at"]