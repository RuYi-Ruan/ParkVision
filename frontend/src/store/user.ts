import { defineStore } from "pinia";
import { computed, ref } from "vue";

import {
  clearToken,
  clearUserProfile,
  getToken,
  getUserProfile,
  setToken as persistToken,
  setUserProfile,
  type PersistedUserProfile,
} from "@/utils/auth";

export const useUserStore = defineStore("user", () => {
  const persistedProfile = getUserProfile();

  // 刷新页面后优先从本地恢复登录态和角色信息，避免权限判断失真。
  const token = ref(getToken());
  const userId = ref(persistedProfile?.id || 0);
  const username = ref(persistedProfile?.username || "");
  const displayName = ref(persistedProfile?.displayName || "系统管理员");
  const role = ref<PersistedUserProfile["role"]>(persistedProfile?.role || "viewer");
  const roleName = ref(persistedProfile?.roleName || "只读用户");

  const isAdmin = computed(() => role.value === "admin");
  const isOperator = computed(() => role.value === "operator");
  const isViewer = computed(() => role.value === "viewer");

  // 业务管理页允许管理员和值班管理员写入，只读账号保留查看能力。
  const canManageBusiness = computed(() => isAdmin.value || isOperator.value);
  const canManageUsers = computed(() => isAdmin.value);
  const canEditSystemConfig = computed(() => isAdmin.value);
  const canViewSystemConfig = computed(() => isAdmin.value || isOperator.value);

  // 角色徽标用于顶部导航显示，让演示时能一眼看出当前账号身份。
  const roleBadge = computed(() => {
    if (isAdmin.value) {
      return "管理员";
    }
    if (isOperator.value) {
      return "值班";
    }
    return "只读";
  });

  // 权限摘要用于说明当前账号能操作到什么范围，避免只能靠按钮显隐理解权限。
  const permissionSummary = computed(() => {
    if (isAdmin.value) {
      return "可管理用户、系统设置及全部业务模块";
    }
    if (isOperator.value) {
      return "可维护车位、车辆与记录，系统设置仅可查看";
    }
    return "仅可查看业务数据与详情，不可执行写操作";
  });

  function setToken(value: string) {
    token.value = value;
    persistToken(value);
  }

  function setProfile(profile: PersistedUserProfile) {
    userId.value = profile.id;
    username.value = profile.username;
    displayName.value = profile.displayName;
    role.value = profile.role;
    roleName.value = profile.roleName;
    setUserProfile(profile);
  }

  function logout() {
    // 登出时同时清空 token 和角色档案，避免刷新后残留旧权限。
    token.value = "";
    userId.value = 0;
    username.value = "";
    displayName.value = "系统管理员";
    role.value = "viewer";
    roleName.value = "只读用户";
    clearToken();
    clearUserProfile();
  }

  return {
    token,
    userId,
    username,
    displayName,
    role,
    roleName,
    isAdmin,
    isOperator,
    isViewer,
    canManageBusiness,
    canManageUsers,
    canEditSystemConfig,
    canViewSystemConfig,
    roleBadge,
    permissionSummary,
    setToken,
    setProfile,
    logout,
  };
});
