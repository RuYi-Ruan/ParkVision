"""users 模块的数据模型。

这里直接映射到已经由 MySQL 手工创建的业务表，不再重复建表。
"""

from django.db import models


class ParkUser(models.Model):
    """系统用户表映射。"""

    username = models.CharField("登录账号", max_length=50, unique=True)
    password = models.CharField("登录密码", max_length=255)
    real_name = models.CharField("真实姓名", max_length=50)
    phone = models.CharField("手机号", max_length=20, blank=True, null=True)
    role = models.CharField("角色", max_length=20, default="admin")
    status = models.SmallIntegerField("状态", default=1)
    last_login = models.DateTimeField("最后登录时间", blank=True, null=True)
    created_at = models.DateTimeField("创建时间")
    updated_at = models.DateTimeField("更新时间")

    class Meta:
        managed = False
        db_table = "pv_users"
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self) -> str:
        return f"{self.username}({self.real_name})"
