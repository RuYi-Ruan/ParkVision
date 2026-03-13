import request, { get, post } from "@/utils/request";
import type { RecordDetailItem, RecordItem, RecordSummary } from "@/types/domain";

// 停车记录列表的筛选条件比通用列表更多，因此单独定义查询类型。
export type RecordListQuery = {
  keyword?: string;
  status?: string;
  payStatus?: string;
  dateFrom?: string;
  dateTo?: string;
};

export type RecordEntryFormData = {
  plate_number: string;
  entry_gate: string;
  space_id?: number;
  remark?: string;
};

export type RecordExitFormData = {
  plate_number: string;
  exit_gate: string;
  remark?: string;
};

export function getRecordList(params?: RecordListQuery) {
  // 停车记录列表优先走真实接口，联调失败时再由页面回退到 mock。
  return get<RecordItem[]>("/records/", { params });
}

export function getRecordSummary(params?: RecordListQuery) {
  // 汇总卡片与记录列表共用同一套筛选条件，保证口径一致。
  return get<RecordSummary>("/records/summary/", { params });
}

export function getRecordDetail(id: number) {
  // 详情接口按主键获取单条记录，便于列表与详情联动。
  return get<RecordDetailItem>(`/records/${id}/`);
}

export function createEntryRecord(data: RecordEntryFormData) {
  // 模拟入场接口用于在未接 YOLO 前先跑通停车业务闭环。
  return post<RecordDetailItem, RecordEntryFormData>("/records/entry/", data);
}

export function settleExitRecord(data: RecordExitFormData) {
  // 模拟出场接口会触发费用结算和车位释放。
  return post<RecordDetailItem, RecordExitFormData>("/records/exit/", data);
}

export async function exportRecordList(params?: RecordListQuery) {
  // 导出接口返回二进制文件流，这里直接返回 blob 供页面触发下载。
  return request.get<never, Blob>("/records/export/", {
    params,
    responseType: "blob",
  });
}
