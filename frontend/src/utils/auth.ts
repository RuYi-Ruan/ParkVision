const TOKEN_KEY = "parkvision-token";
const USER_ID_KEY = "parkvision-user-id";
const USERNAME_KEY = "parkvision-username";
const DISPLAY_NAME_KEY = "parkvision-display-name";
const ROLE_KEY = "parkvision-role";
const ROLE_NAME_KEY = "parkvision-role-name";

export type PersistedUserProfile = {
  id: number;
  username: string;
  displayName: string;
  role: "admin" | "operator" | "viewer";
  roleName: string;
};

export function getToken() {
  // 统一返回字符串，避免调用方额外处理 null 分支。
  return localStorage.getItem(TOKEN_KEY) || "";
}

export function setToken(token: string) {
  // token 单独持久化，方便请求拦截器和路由守卫直接读取。
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function getUserRole() {
  // 角色值用于前端权限控制，刷新页面后依旧可恢复。
  return (localStorage.getItem(ROLE_KEY) || "") as PersistedUserProfile["role"] | "";
}

export function getUserProfile(): PersistedUserProfile | null {
  const id = Number(localStorage.getItem(USER_ID_KEY) || 0);
  const username = localStorage.getItem(USERNAME_KEY) || "";
  const displayName = localStorage.getItem(DISPLAY_NAME_KEY) || "";
  const role = getUserRole();
  const roleName = localStorage.getItem(ROLE_NAME_KEY) || "";

  if (!id || !username || !displayName || !role || !roleName) {
    return null;
  }

  return {
    id,
    username,
    displayName,
    role,
    roleName,
  };
}

export function setUserProfile(profile: PersistedUserProfile) {
  // 将登录用户档案统一写入本地，保证页面刷新后仍能恢复权限信息。
  localStorage.setItem(USER_ID_KEY, String(profile.id));
  localStorage.setItem(USERNAME_KEY, profile.username);
  localStorage.setItem(DISPLAY_NAME_KEY, profile.displayName);
  localStorage.setItem(ROLE_KEY, profile.role);
  localStorage.setItem(ROLE_NAME_KEY, profile.roleName);
}

export function clearUserProfile() {
  localStorage.removeItem(USER_ID_KEY);
  localStorage.removeItem(USERNAME_KEY);
  localStorage.removeItem(DISPLAY_NAME_KEY);
  localStorage.removeItem(ROLE_KEY);
  localStorage.removeItem(ROLE_NAME_KEY);
}
