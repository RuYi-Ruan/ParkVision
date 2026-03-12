const TOKEN_KEY = "parkvision-token";

export function getToken() {
  // 统一返回字符串，路由守卫和状态仓库就不需要额外处理 null。
  return localStorage.getItem(TOKEN_KEY) || "";
}

export function setToken(token: string) {
  // 将 token 持久化逻辑收敛在这里，后续切换存储方式时改动更小。
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}
