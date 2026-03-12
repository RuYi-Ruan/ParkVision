import type { MonitorBlock, ParkingSpace } from "./types";

// 车位状态筛选项与页面按钮保持一一对应。
export const parkingStatusFilters = [
  { label: "全部", value: "all" },
  { label: "空闲", value: "free" },
  { label: "占用", value: "busy" },
  { label: "维护", value: "warning" },
] as const;

export const parkingSpaces: ParkingSpace[] = [
  { id: 1, code: "A-01", zone: "A 区地面", status: "空闲", updatedAt: "09:18", type: "free", spaceType: "普通车位", floorNo: "1F", remark: "" },
  { id: 2, code: "A-02", zone: "A 区地面", status: "占用", updatedAt: "09:12", type: "busy", spaceType: "普通车位", floorNo: "1F", remark: "" },
  { id: 3, code: "B-08", zone: "B 区地面", status: "空闲", updatedAt: "09:10", type: "free", spaceType: "普通车位", floorNo: "1F", remark: "" },
  { id: 4, code: "C-15", zone: "地下 C 区", status: "维护", updatedAt: "08:40", type: "warning", spaceType: "普通车位", floorNo: "B1", remark: "设备维护中" },
  { id: 5, code: "D-03", zone: "地下 D 区", status: "占用", updatedAt: "08:21", type: "busy", spaceType: "普通车位", floorNo: "B1", remark: "" },
  { id: 6, code: "D-09", zone: "地下 D 区", status: "空闲", updatedAt: "08:18", type: "free", spaceType: "新能源车位", floorNo: "B1", remark: "带充电桩" },
];

export const parkingMonitorBlocks: MonitorBlock[] = [
  { name: "A 区入口视角", camera: "CAM-01", rate: "38%" },
  { name: "B 区俯视视角", camera: "CAM-03", rate: "72%" },
  { name: "地下车库视角", camera: "CAM-05", rate: "81%" },
  { name: "出口通道视角", camera: "CAM-08", rate: "29%" },
];
