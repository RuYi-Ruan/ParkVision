import request from "@/utils/request";

export function getParkingSpaces() {
  return request.get("/parking/");
}
