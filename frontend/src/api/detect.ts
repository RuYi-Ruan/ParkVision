import { get, post } from "@/utils/request";
import type { DetectResult } from "@/types/domain";

export function getDetectPresets() {
  // 识别测试页先读取后端预设列表，后续可以无缝替换成真实历史样例。
  return get<DetectResult[]>("/detection/");
}

export function detectImage(data: FormData) {
  // 识别接口保留 FormData 形态，方便后续直接上传真实图片文件。
  return post<DetectResult, FormData>("/detection/", data);
}
