import { get, put } from "@/utils/request";
import type { SystemConfigData } from "@/types/domain";

export function getSystemConfig() {
  // 设置页初始化时读取当前已保存的系统配置。
  return get<SystemConfigData>("/system-config/");
}

export function updateSystemConfig(data: Omit<SystemConfigData, "updated_at">) {
  // 保存时只提交可编辑字段，更新时间由后端统一生成。
  return put<SystemConfigData, Omit<SystemConfigData, "updated_at">>("/system-config/", data);
}
