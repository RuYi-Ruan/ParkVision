import { get } from "@/utils/request";
import type { ListQuery } from "@/types/api";
import type { RecordDetailItem, RecordItem } from "@/types/domain";

export function getRecordList(params?: ListQuery) {
  // 停车记录页沿用统一的列表查询结构，保持多页面交互一致。
  return get<RecordItem[]>("/records/", { params });
}

export function getRecordDetail(id: number) {
  // 详情接口按主键获取单条记录，便于列表和详情页解耦。
  return get<RecordDetailItem>(`/records/${id}/`);
}
