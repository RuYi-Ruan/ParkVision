import { del, get, post, put } from "@/utils/request";
import type { ListQuery } from "@/types/api";
import type { ParkingMonitorItem, ParkingSpaceItem } from "@/types/domain";

export type ParkingSpaceFormData = {
  space_code: string;
  area_code: string;
  space_type: string;
  status: string;
  floor_no?: string;
  remark?: string;
};

export function getParkingSpaces(params?: ListQuery) {
  // 车位列表的筛选参数与页面工具栏一一对应，方便后续继续扩展。
  return get<ParkingSpaceItem[]>("/parking/", { params });
}

export function createParkingSpace(data: ParkingSpaceFormData) {
  // 新增车位使用与后端写入序列化器一致的字段命名。
  return post<ParkingSpaceItem, ParkingSpaceFormData>("/parking/", data);
}

export function updateParkingSpace(id: number, data: ParkingSpaceFormData) {
  // 编辑车位时通过主键定位记录，保持接口语义清晰。
  return put<ParkingSpaceItem, ParkingSpaceFormData>(`/parking/${id}/`, data);
}

export function deleteParkingSpace(id: number) {
  // 删除接口只返回统一响应消息，不再单独携带实体数据。
  return del<null>(`/parking/${id}/`);
}

export function getParkingMonitor() {
  // 监控卡片单独请求，便于车位列表页和监控页拆分演进。
  return get<ParkingMonitorItem[]>("/parking/monitor/");
}
