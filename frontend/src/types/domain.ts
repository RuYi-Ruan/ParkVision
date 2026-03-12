// 领域类型统一描述前后端之间交换的数据结构，
// 后续替换 mock 或扩展真实接口时都以这里为准。
export type UserProfile = {
  username: string;
  role_name: string;
  token: string;
};

export type DashboardMetric = {
  label: string;
  value: string;
};

export type DashboardOverview = {
  eyebrow: string;
  title: string;
  description: string;
  metrics: DashboardMetric[];
};

export type DashboardStatItem = {
  label: string;
  value: string | number;
  trend: string;
  footnote: string;
  type: "positive" | "neutral" | "warning";
};

export type RecentRecordItem = {
  plate: string;
  time: string;
  gate: string;
};

export type ParkingSpaceItem = {
  id: number;
  code: string;
  zone: string;
  spaceType?: string;
  status: string;
  updatedAt: string;
  type: "free" | "busy" | "warning";
  floorNo?: string;
  remark?: string;
};

export type ParkingMonitorItem = {
  name: string;
  camera: string;
  rate: string;
};

export type RecordItem = {
  id: number;
  recordNo: string;
  plate: string;
  enterAt: string;
  leaveAt: string;
  duration: string;
  status: string;
  type: "busy" | "free" | "warning";
};

export type RecordDetailItem = {
  id: number;
  recordNo: string;
  plate: string;
  entryGate: string;
  exitGate: string;
  enterAt: string;
  leaveAt: string;
  duration: string;
  amount: string;
  payStatus: string;
  status: string;
  remark: string;
  entryImage: string;
  exitImage: string;
};

export type VehicleItem = {
  id: number;
  plate: string;
  owner: string;
  ownerPhone?: string;
  category: string;
  color?: string;
  space: string;
  status: string;
  statusValue?: number;
  type: "free" | "warning";
};

export type DetectStep = {
  label: string;
  value: string;
};

export type DetectResult = {
  id: string;
  label: string;
  plate: string;
  task: string;
  confidence: string;
  vehicleType: string;
  location: string;
  boxStyle: Record<string, string>;
  steps: DetectStep[];
};

export type SystemSettingItem = {
  label: string;
  value: string;
  desc: string;
};
