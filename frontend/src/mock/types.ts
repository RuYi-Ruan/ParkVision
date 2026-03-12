export type TrendType = "positive" | "neutral" | "warning";
export type SpaceState = "free" | "busy" | "warning";
export type RecordState = "busy" | "free";
export type VehicleState = "free" | "warning";

export type DashboardStat = {
  label: string;
  value: string | number;
  trend: string;
  footnote: string;
  type: TrendType;
};

export type DashboardRecord = {
  plate: string;
  time: string;
  gate: string;
};

export type SpaceBlock = {
  title: string;
  status: string;
  camera: string;
  statusType: SpaceState;
};

export type ParkingSpace = {
  id: number;
  code: string;
  zone: string;
  spaceType?: string;
  status: string;
  updatedAt: string;
  type: SpaceState;
  floorNo?: string;
  remark?: string;
};

export type MonitorBlock = {
  name: string;
  camera: string;
  rate: string;
};

export type ParkingRecord = {
  plate: string;
  enterAt: string;
  leaveAt: string;
  duration: string;
  status: string;
  type: RecordState;
};

export type Vehicle = {
  id: number;
  plate: string;
  owner: string;
  category: string;
  space: string;
  status: string;
  type: VehicleState;
};

export type DetectPreset = {
  id: string;
  label: string;
  plate: string;
  task: string;
  confidence: string;
  vehicleType: string;
  location: string;
  boxStyle: Record<string, string>;
  steps: Array<{ label: string; value: string }>;
};

export type SystemSetting = {
  label: string;
  value: string;
  desc: string;
};
