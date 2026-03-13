import { post } from "@/utils/request";
import type { UserProfile } from "@/types/domain";

export function login(data: { username: string; password: string }) {
  // 登录接口已经切到真实数据库校验，返回结果同时包含角色信息，
  // 便于前端在登录后立即恢复菜单与按钮权限。
  return post<UserProfile, typeof data>("/users/", data);
}
