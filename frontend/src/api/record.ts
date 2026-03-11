import request from "@/utils/request";

export function getRecordList() {
  return request.get("/records/");
}
