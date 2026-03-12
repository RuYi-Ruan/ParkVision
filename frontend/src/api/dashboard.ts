import { get } from "@/utils/request";
import type { DashboardOverview, DashboardStatItem, RecentRecordItem } from "@/types/domain";

export function getDashboardData() {
  // 首页将概览、统计卡片和最近记录合并为一次请求，减少页面装配成本。
  return get<{
    overview: DashboardOverview;
    stats: DashboardStatItem[];
    recent_records: RecentRecordItem[];
  }>("/dashboard/");
}
