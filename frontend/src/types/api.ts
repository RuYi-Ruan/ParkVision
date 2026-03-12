// 统一的接口响应类型定义。
export type ApiResponse<T> = {
  code: number;
  message: string;
  data: T;
};

// 列表页通用查询参数，目前主要用于关键词和状态筛选。
export type ListQuery = {
  keyword?: string;
  status?: string;
};
