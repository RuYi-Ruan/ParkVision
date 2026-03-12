import { defineStore } from "pinia";
import { ref } from "vue";

import { clearToken, getToken, setToken as persistToken } from "@/utils/auth";

export const useUserStore = defineStore("user", () => {
  // 刷新页面后优先从本地恢复 token，避免已登录用户被错误踢回登录页。
  const token = ref(getToken());
  const username = ref("系统管理员");
  const roleName = ref("值班管理");

  function setToken(value: string) {
    token.value = value;
    persistToken(value);
  }

  function setProfile(name: string, role: string) {
    // 用户名和角色名单独维护，便于头部区域直接消费。
    username.value = name;
    roleName.value = role;
  }

  function logout() {
    // 清空 token 后，路由守卫会自然把用户带回登录流程。
    token.value = "";
    clearToken();
  }

  return {
    token,
    username,
    roleName,
    setToken,
    setProfile,
    logout,
  };
});
