"""vehicles 模块的数据模型。"""

from django.db import models

from apps.users.models import ParkUser


class Vehicle(models.Model):
    """车辆信息表映射。"""

    plate_number = models.CharField("车牌号", max_length=20, unique=True)
    owner_name = models.CharField("车主姓名", max_length=50)
    owner_phone = models.CharField("车主电话", max_length=20, blank=True, null=True)
    vehicle_type = models.CharField("车辆类型", max_length=20, default="小型车")
    color = models.CharField("车身颜色", max_length=20, blank=True, null=True)
    user = models.ForeignKey(
        ParkUser,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        db_column="user_id",
        related_name="vehicles",
        verbose_name="绑定用户",
    )
    status = models.SmallIntegerField("状态", default=1)
    remark = models.CharField("备注", max_length=255, blank=True, null=True)
    created_at = models.DateTimeField("创建时间")
    updated_at = models.DateTimeField("更新时间")

    class Meta:
        managed = False
        db_table = "pv_vehicles"
        verbose_name = "车辆"
        verbose_name_plural = "车辆"

    def __str__(self) -> str:
        return self.plate_number
