import request from "@/utils/request";

export function getVehicleList() {
  return request.get("/vehicles/");
}
