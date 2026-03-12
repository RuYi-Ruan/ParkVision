import { post } from "@/utils/request";
import type { UserProfile } from "@/types/domain";

export function login(data: { username: string; password: string }) {
  // 登录接口虽然目前接的是演示账号校验，但路径和返回结构已经按正式接口设计。
  return post<UserProfile, typeof data>("/users/", data);
}
