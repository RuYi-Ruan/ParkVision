// 领域类型统一描述前后端之间交换的数据结构。
// 后续替换 mock 或扩展真实接口时，都以这里为准。

export type UserRole = "admin" | "operator" | "viewer";

export type UserProfile = {
  id: number;
  username: string;
  displayName: string;
  role: UserRole;
  roleName: string;
  token: string;
};

export type UserItem = {
  id: number;
  username: string;
  realName: string;
  phone: string;
  role: UserRole;
  roleName: string;
  status: string;
  statusValue: number;
  type: "free" | "warning";
  lastLogin: string;
  createdAt: string;
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
  id?: number;
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

export type ParkingSpaceRecentRecordItem = {
  id: number;
  recordNo: string;
  plate: string;
  enterAt: string;
  leaveAt: string;
  duration: string;
  status: string;
  type: "busy" | "free" | "warning";
  amount: string;
};

export type ParkingSpaceDetailItem = {
  id: number;
  code: string;
  zone: string;
  spaceType: string;
  status: string;
  type: "free" | "busy" | "warning";
  floorNo: string;
  remark: string;
  createdAt: string;
  updatedAt: string;
  currentPlate: string;
  currentRecordId?: number | null;
  recentRecords: ParkingSpaceRecentRecordItem[];
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
  amount: string;
  payStatus: string;
  status: string;
  type: "busy" | "free" | "warning";
};

export type RecordDetailItem = {
  id: number;
  recordNo: string;
  vehicleId?: number | null;
  plate: string;
  entryGate: string;
  exitGate: string;
  enterAt: string;
  leaveAt: string;
  duration: string;
  amount: string;
  payStatus: string;
  status: string;
  pricingNote: string;
  remark: string;
  entryImage: string;
  exitImage: string;
};

export type RecordSummary = {
  totalCount: number;
  inLotCount: number;
  departedCount: number;
  unpaidCount: number;
  overdueCount: number;
  totalAmount: string;
  ruleSummary: string;
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

export type VehicleRecentRecordItem = {
  id: number;
  recordNo: string;
  enterAt: string;
  leaveAt: string;
  duration: string;
  status: string;
  type: "busy" | "free" | "warning";
  amount: string;
};

export type VehicleDetailItem = {
  id: number;
  plate: string;
  owner: string;
  ownerPhone: string;
  category: string;
  color: string;
  status: string;
  type: "free" | "warning";
  remark: string;
  createdAt: string;
  updatedAt: string;
  currentRecordId?: number | null;
  recentRecords: VehicleRecentRecordItem[];
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

export type SystemConfigData = {
  parking_rule: {
    free_minutes: number;
    fee_per_hour: string;
    daily_cap: string;
    overdue_hours: number;
  };
  recognition: {
    detect_confidence: string;
    ocr_confidence: string;
    yolo_model_path: string;
    plate_model_path: string;
  };
  runtime: {
    default_zone: string;
    monitor_refresh_seconds: number;
    auto_export_days: number;
    retain_days: number;
  };
  updated_at?: string;
};
