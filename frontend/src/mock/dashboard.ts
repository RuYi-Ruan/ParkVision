import type { DashboardRecord, DashboardStat, SpaceBlock } from "./types";

// 首页 mock 数据集中维护，后续替换真实接口时可以按字段一一映射。
export const dashboardHero = {
  eyebrow: "今日运营概览",
  title: "停车场状态稳定，识别链路在线。",
  description: "当前页面用于展示系统首页的设计方向，后续可直接替换为真实接口数据。",
  metrics: [
    { label: "峰值占用率", value: "83%" },
    { label: "平均停留时长", value: "2.4h" },
  ],
};

export const dashboardStats: DashboardStat[] = [
  { label: "总车位", value: "120", trend: "+4.2%", footnote: "本周车位已全部投用", type: "positive" },
  { label: "空闲车位", value: "46", trend: "实时", footnote: "A 区空闲较多", type: "neutral" },
  { label: "在场车辆", value: "74", trend: "-2.1%", footnote: "晚高峰后逐步下降", type: "warning" },
  { label: "今日进场", value: "218", trend: "+18", footnote: "较昨日同期增长", type: "positive" },
];

export const dashboardSpaceBlocks: SpaceBlock[] = [
  { title: "A-01 至 A-20", status: "空闲 8", camera: "A01", statusType: "free" },
  { title: "B-01 至 B-20", status: "占用 17", camera: "B02", statusType: "busy" },
  { title: "C-01 至 C-20", status: "巡检中", camera: "C03", statusType: "warning" },
];

export const dashboardRecentRecords: DashboardRecord[] = [
  { plate: "粤B·A2138", time: "09:12", gate: "东入口" },
  { plate: "粤B·Q8M61", time: "09:07", gate: "南入口" },
  { plate: "粤B·7P221", time: "08:55", gate: "西入口" },
  { plate: "粤B·D9C12", time: "08:41", gate: "地下车库" },
];
