import type { ParkingMonitorItem, ParkingSpaceDetailItem, ParkingSpaceItem } from "@/types/domain";

// 车位状态筛选项与页面按钮保持一一对应。
export const parkingStatusFilters = [
  { label: "全部", value: "all" },
  { label: "空闲", value: "free" },
  { label: "占用", value: "busy" },
  { label: "维护", value: "warning" },
] as const;

export const parkingSpaces: ParkingSpaceItem[] = [
  { id: 1, code: "A-01", zone: "A 区地面", status: "空闲", updatedAt: "09:18", type: "free", spaceType: "普通车位", floorNo: "1F", remark: "" },
  { id: 2, code: "A-02", zone: "A 区地面", status: "占用", updatedAt: "09:12", type: "busy", spaceType: "普通车位", floorNo: "1F", remark: "" },
  { id: 3, code: "B-08", zone: "B 区地面", status: "空闲", updatedAt: "09:10", type: "free", spaceType: "普通车位", floorNo: "1F", remark: "" },
  { id: 4, code: "C-15", zone: "地下 C 区", status: "维护", updatedAt: "08:40", type: "warning", spaceType: "普通车位", floorNo: "B1", remark: "设备维护中" },
  { id: 5, code: "D-03", zone: "地下 D 区", status: "占用", updatedAt: "08:21", type: "busy", spaceType: "普通车位", floorNo: "B1", remark: "" },
  { id: 6, code: "D-09", zone: "地下 D 区", status: "空闲", updatedAt: "08:18", type: "free", spaceType: "新能源车位", floorNo: "B1", remark: "带充电桩" },
];

// 车位详情页兜底数据，结构与后端详情接口保持一致。
export const parkingSpaceDetails: ParkingSpaceDetailItem[] = [
  {
    id: 1,
    code: "A-01",
    zone: "A 区地面",
    spaceType: "普通车位",
    status: "空闲",
    type: "free",
    floorNo: "1F",
    remark: "暂无备注",
    createdAt: "2026-03-08 09:00",
    updatedAt: "2026-03-12 09:18",
    currentPlate: "--",
    currentRecordId: null,
    recentRecords: [],
  },
  {
    id: 2,
    code: "A-02",
    zone: "A 区地面",
    spaceType: "普通车位",
    status: "占用",
    type: "busy",
    floorNo: "1F",
    remark: "暂无备注",
    createdAt: "2026-03-08 09:02",
    updatedAt: "2026-03-12 09:12",
    currentPlate: "粤B·A2138",
    currentRecordId: 1,
    recentRecords: [
      {
        id: 1,
        recordNo: "REC202603120001",
        plate: "粤B·A2138",
        enterAt: "2026-03-12 09:12",
        leaveAt: "--",
        duration: "进行中",
        status: "在场",
        type: "busy",
        amount: "0.00",
      },
    ],
  },
  {
    id: 4,
    code: "C-15",
    zone: "地下 C 区",
    spaceType: "普通车位",
    status: "维护",
    type: "warning",
    floorNo: "B1",
    remark: "设备维护中",
    createdAt: "2026-03-08 09:08",
    updatedAt: "2026-03-12 08:40",
    currentPlate: "--",
    currentRecordId: null,
    recentRecords: [],
  },
  {
    id: 5,
    code: "D-03",
    zone: "地下 D 区",
    spaceType: "普通车位",
    status: "占用",
    type: "busy",
    floorNo: "B1",
    remark: "暂无备注",
    createdAt: "2026-03-08 09:10",
    updatedAt: "2026-03-12 08:21",
    currentPlate: "粤B·Q8M61",
    currentRecordId: 2,
    recentRecords: [
      {
        id: 2,
        recordNo: "REC202603120002",
        plate: "粤B·Q8M61",
        enterAt: "2026-03-12 09:07",
        leaveAt: "--",
        duration: "进行中",
        status: "在场",
        type: "busy",
        amount: "0.00",
      },
    ],
  },
];

export const parkingMonitorBlocks: ParkingMonitorItem[] = [
  { name: "A 区入口视角", camera: "CAM-01", rate: "38%" },
  { name: "B 区俯视视角", camera: "CAM-03", rate: "72%" },
  { name: "地下车库视角", camera: "CAM-05", rate: "81%" },
  { name: "出口通道视角", camera: "CAM-08", rate: "29%" },
];
