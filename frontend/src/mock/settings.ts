import type { SystemConfigData } from "@/types/domain";

// 系统设置的本地兜底数据，与后端接口结构保持一致。
export const systemConfigMock: SystemConfigData = {
  parking_rule: {
    free_minutes: 15,
    fee_per_hour: "6.00",
    daily_cap: "48.00",
    overdue_hours: 24,
  },
  recognition: {
    detect_confidence: "0.45",
    ocr_confidence: "0.60",
    yolo_model_path: "ai/weights/vehicle_yolo.pt",
    plate_model_path: "ai/weights/plate_yolo.pt",
  },
  runtime: {
    default_zone: "主停车区 A 区",
    monitor_refresh_seconds: 30,
    auto_export_days: 30,
    retain_days: 365,
  },
  updated_at: "2026-03-13 18:00",
};
