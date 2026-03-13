import type { UserItem } from "@/types/domain";

// 用户状态筛选项与页面按钮保持一致。
export const userStatusFilters = [
  { label: "全部", value: "all" },
  { label: "启用", value: "free" },
  { label: "停用", value: "warning" },
] as const;

// 角色筛选项用于快速切换管理员、值班管理员和只读用户。
export const userRoleFilters = [
  { label: "全部角色", value: "all" },
  { label: "系统管理员", value: "admin" },
  { label: "值班管理员", value: "operator" },
  { label: "只读用户", value: "viewer" },
] as const;

// 用户管理页的本地演示数据。
export const usersMock: UserItem[] = [
  {
    id: 1,
    username: "admin",
    realName: "系统管理员",
    phone: "13800000000",
    role: "admin",
    roleName: "系统管理员",
    status: "启用",
    statusValue: 1,
    type: "free",
    lastLogin: "2026-03-13 10:20",
    createdAt: "2026-03-01 09:00",
  },
  {
    id: 2,
    username: "operator01",
    realName: "值班管理员",
    phone: "13800000001",
    role: "operator",
    roleName: "值班管理员",
    status: "启用",
    statusValue: 1,
    type: "free",
    lastLogin: "2026-03-13 08:45",
    createdAt: "2026-03-03 10:30",
  },
  {
    id: 3,
    username: "viewer01",
    realName: "演示账号",
    phone: "13800000002",
    role: "viewer",
    roleName: "只读用户",
    status: "启用",
    statusValue: 1,
    type: "free",
    lastLogin: "2026-03-12 18:20",
    createdAt: "2026-03-05 14:10",
  },
];
