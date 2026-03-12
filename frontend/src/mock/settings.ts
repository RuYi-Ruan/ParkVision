import type { SystemSetting } from "./types";

export const systemSettings: SystemSetting[] = [
  { label: "后端接口", value: "127.0.0.1:8000", desc: "当前开发环境 API 地址。" },
  { label: "识别服务", value: "待接入", desc: "后续连接 AI 推理模块。" },
  { label: "默认园区", value: "主停车区 A 区", desc: "用于后台首页初始展示。" },
];
