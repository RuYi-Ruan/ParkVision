import { createRouter, createWebHistory } from "vue-router";

import AppLayout from "@/layout/index.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: () => import("@/views/login/Login.vue"),
      meta: { title: "登录" },
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
          meta: { title: "首页统计" },
        },
        {
          path: "parking/spaces",
          name: "space-list",
          component: () => import("@/views/parking/SpaceList.vue"),
          meta: { title: "车位列表" },
        },
        {
          path: "parking/monitor",
          name: "space-monitor",
          component: () => import("@/views/parking/SpaceMonitor.vue"),
          meta: { title: "车位监控" },
        },
        {
          path: "records",
          name: "record-list",
          component: () => import("@/views/records/RecordList.vue"),
          meta: { title: "停车记录" },
        },
        {
          path: "records/:id",
          name: "record-detail",
          component: () => import("@/views/records/RecordDetail.vue"),
          meta: { title: "记录详情" },
        },
        {
          path: "vehicles",
          name: "vehicle-list",
          component: () => import("@/views/vehicles/VehicleList.vue"),
          meta: { title: "车辆管理" },
        },
        {
          path: "detection",
          name: "detect-test",
          component: () => import("@/views/detection/DetectTest.vue"),
          meta: { title: "识别测试" },
        },
        {
          path: "settings",
          name: "system-config",
          component: () => import("@/views/settings/SystemConfig.vue"),
          meta: { title: "系统设置" },
        },
      ],
    },
  ],
});

router.afterEach((to) => {
  document.title = `${to.meta.title ?? "ParkVision"} - ParkVision`;
});

export default router;
