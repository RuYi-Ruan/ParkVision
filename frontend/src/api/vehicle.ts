import { del, get, post, put } from "@/utils/request";
import type { ListQuery } from "@/types/api";
import type { VehicleItem } from "@/types/domain";

export type VehicleFormData = {
  plate_number: string;
  owner_name: string;
  owner_phone?: string;
  vehicle_type: string;
  color?: string;
  status: number;
  remark?: string;
};

export function getVehicleList(params?: ListQuery) {
  // 车辆管理当前以列表读取为主，并逐步扩展到完整管理能力。
  return get<VehicleItem[]>("/vehicles/", { params });
}

export function createVehicle(data: VehicleFormData) {
  // 新增车辆使用与后端写入序列化器一致的字段命名。
  return post<VehicleItem, VehicleFormData>("/vehicles/", data);
}

export function updateVehicle(id: number, data: VehicleFormData) {
  // 编辑车辆时通过主键定位记录，保持接口语义清晰。
  return put<VehicleItem, VehicleFormData>(`/vehicles/${id}/`, data);
}

export function deleteVehicle(id: number) {
  // 删除接口只返回统一响应消息，不再单独携带实体数据。
  return del<null>(`/vehicles/${id}/`);
}
