"""records 模块的数据模型。"""

from django.db import models

from apps.parking.models import ParkingSpace
from apps.vehicles.models import Vehicle


class ParkingRecord(models.Model):
    """停车记录表映射。"""

    record_no = models.CharField("记录编号", max_length=50, unique=True)
    plate_number = models.CharField("车牌号", max_length=20)
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        db_column="vehicle_id",
        related_name="parking_records",
        verbose_name="车辆",
    )
    space = models.ForeignKey(
        ParkingSpace,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        db_column="space_id",
        related_name="parking_records",
        verbose_name="车位",
    )
    entry_gate = models.CharField("入口", max_length=50, blank=True, null=True)
    exit_gate = models.CharField("出口", max_length=50, blank=True, null=True)
    entry_time = models.DateTimeField("入场时间")
    exit_time = models.DateTimeField("出场时间", blank=True, null=True)
    duration_minutes = models.IntegerField("停车时长", default=0)
    amount = models.DecimalField("停车费用", max_digits=10, decimal_places=2, default=0)
    pay_status = models.CharField("支付状态", max_length=20, default="未支付")
    record_status = models.CharField("记录状态", max_length=20, default="在场")
    entry_image = models.CharField("入场图片", max_length=255, blank=True, null=True)
    exit_image = models.CharField("出场图片", max_length=255, blank=True, null=True)
    remark = models.CharField("备注", max_length=255, blank=True, null=True)
    created_at = models.DateTimeField("创建时间")
    updated_at = models.DateTimeField("更新时间")

    class Meta:
        managed = False
        db_table = "pv_parking_records"
        verbose_name = "停车记录"
        verbose_name_plural = "停车记录"

    def __str__(self) -> str:
        return self.record_no
