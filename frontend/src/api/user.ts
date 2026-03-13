import { del, get, post, put } from "@/utils/request";
import type { UserItem } from "@/types/domain";

export type UserListQuery = {
  keyword?: string;
  status?: string;
  role?: string;
};

export type UserFormData = {
  username: string;
  password: string;
  real_name: string;
  phone?: string;
  role: "admin" | "operator" | "viewer";
  status: number;
};

export function getUserList(params?: UserListQuery) {
  // 用户管理列表与登录接口拆开，避免认证和后台管理耦合。
  return get<UserItem[]>("/users/manage/", { params });
}

export function createUser(data: UserFormData) {
  return post<UserItem, UserFormData>("/users/manage/", data);
}

export function updateUser(id: number, data: UserFormData) {
  return put<UserItem, UserFormData>(`/users/manage/${id}/`, data);
}

export function deleteUser(id: number) {
  return del<null>(`/users/manage/${id}/`);
}
