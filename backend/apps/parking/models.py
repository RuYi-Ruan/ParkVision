"""parking 模块的数据模型。"""

from django.db import models


class ParkingSpace(models.Model):
    """车位信息表映射。"""

    space_code = models.CharField("车位编号", max_length=20, unique=True)
    area_code = models.CharField("区域编码", max_length=20)
    space_type = models.CharField("车位类型", max_length=20, default="普通车位")
    status = models.CharField("状态", max_length=20, default="空闲")
    floor_no = models.CharField("楼层", max_length=20, blank=True, null=True)
    remark = models.CharField("备注", max_length=255, blank=True, null=True)
    created_at = models.DateTimeField("创建时间")
    updated_at = models.DateTimeField("更新时间")

    class Meta:
        managed = False
        db_table = "pv_parking_spaces"
        verbose_name = "车位"
        verbose_name_plural = "车位"

    def __str__(self) -> str:
        return self.space_code
