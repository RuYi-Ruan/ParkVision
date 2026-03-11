import request from "@/utils/request";

export function detectImage() {
  return request.get("/detection/");
}
