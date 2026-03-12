import axios from "axios";
import type { AxiosRequestConfig } from "axios";

import type { ApiResponse } from "@/types/api";

// 统一创建 axios 实例，避免每个接口文件重复配置 baseURL 和超时时间。
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
});

request.interceptors.response.use(
  // 后端已经约定返回统一结构，这里直接取 response.data，
  // 让业务代码只面对项目自己的响应格式。
  (response) => response.data,
  (error) => Promise.reject(error),
);

export function get<T>(url: string, config?: AxiosRequestConfig) {
  // 第二个泛型用于声明拦截器处理后的最终返回类型。
  return request.get<never, ApiResponse<T>>(url, config);
}

export function post<T, D = unknown>(url: string, data?: D, config?: AxiosRequestConfig<D>) {
  return request.post<never, ApiResponse<T>, D>(url, data, config);
}

export function put<T, D = unknown>(url: string, data?: D, config?: AxiosRequestConfig<D>) {
  return request.put<never, ApiResponse<T>, D>(url, data, config);
}

export function del<T>(url: string, config?: AxiosRequestConfig) {
  return request.delete<never, ApiResponse<T>>(url, config);
}

export default request;
