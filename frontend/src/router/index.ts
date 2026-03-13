import { createRouter, createWebHistory } from "vue-router";

import AppLayout from "@/layout/index.vue";
import { getToken, getUserRole } from "@/utils/auth";
import type { UserRole } from "@/types/domain";

type RouteRoleMeta = {
  title: string;
  public?: boolean;
  roles?: UserRole[];
};

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/login/Login.vue"),
      meta: { title: "登录", public: true } satisfies RouteRoleMeta,
    },
    {
      path: "/",
      component: AppLayout,
      redirect: "/dashboard",
      children: [
        {
          path: "dashboard",
          name: "dashboard",
          component: () => import("@/views/dashboard/Index.vue"),
          meta: { title: "仪表盘" } satisfies RouteRoleMeta,
        },
        {
          path: "parking/spaces",
          name: "space-list",
          component: () => import("@/views/parking/SpaceList.vue"),
          meta: { title: "车位管理" } satisfies RouteRoleMeta,
        },
        {
          path: "parking/spaces/:id",
          name: "space-detail",
          component: () => import("@/views/parking/SpaceDetail.vue"),
          meta: { title: "车位详情" } satisfies RouteRoleMeta,
        },
        {
          path: "parking/monitor",
          name: "space-monitor",
          component: () => import("@/views/parking/SpaceMonitor.vue"),
          meta: { title: "车位监控" } satisfies RouteRoleMeta,
        },
        {
          path: "records",
          name: "record-list",
          component: () => import("@/views/records/RecordList.vue"),
          meta: { title: "停车记录" } satisfies RouteRoleMeta,
        },
        {
          path: "records/:id",
          name: "record-detail",
          component: () => import("@/views/records/RecordDetail.vue"),
          meta: { title: "记录详情" } satisfies RouteRoleMeta,
        },
        {
          path: "vehicles",
          name: "vehicle-list",
          component: () => import("@/views/vehicles/VehicleList.vue"),
          meta: { title: "车辆管理" } satisfies RouteRoleMeta,
        },
        {
          path: "vehicles/:id",
          name: "vehicle-detail",
          component: () => import("@/views/vehicles/VehicleDetail.vue"),
          meta: { title: "车辆详情" } satisfies RouteRoleMeta,
        },
        {
          path: "users",
          name: "user-list",
          component: () => import("@/views/users/UserList.vue"),
          meta: { title: "用户管理", roles: ["admin"] } satisfies RouteRoleMeta,
        },
        {
          path: "detection",
          name: "detect-test",
          component: () => import("@/views/detection/DetectTest.vue"),
          meta: { title: "识别测试", roles: ["admin", "operator"] } satisfies RouteRoleMeta,
        },
        {
          path: "settings",
          name: "system-config",
          component: () => import("@/views/settings/SystemConfig.vue"),
          meta: { title: "系统设置", roles: ["admin", "operator"] } satisfies RouteRoleMeta,
        },
      ],
    },
  ],
});

router.beforeEach((to) => {
  // 当前阶段仍以 token 是否存在作为最轻量的登录判断依据。
  const hasToken = Boolean(getToken());
  const isPublic = Boolean(to.meta.public);

  if (!hasToken && !isPublic) {
    return {
      path: "/login",
      query: { redirect: to.fullPath },
    };
  }

  if (hasToken && to.path === "/login") {
    return "/dashboard";
  }

  const allowedRoles = Array.isArray(to.meta.roles) ? (to.meta.roles as UserRole[]) : [];
  if (allowedRoles.length > 0) {
    const currentRole = getUserRole();
    if (!currentRole || !allowedRoles.includes(currentRole)) {
      return "/dashboard";
    }
  }

  return true;
});

router.afterEach((to) => {
  // 路由切换后同步更新页面标题，便于演示时保持界面完整度。
  document.title = `${String(to.meta.title ?? "ParkVision")} | ParkVision`;
});

export default router;
