<template>
  <aside class="sidebar" :style="{ width: appStore.sidebarWidth }">
    <div class="sidebar__brand-card">
      <div class="sidebar__brand-mark">PV</div>
      <div v-show="!appStore.collapsed" class="sidebar__brand-copy">
        <strong>ParkVision</strong>
        <span>智慧停车平台</span>
      </div>
    </div>

    <div v-show="!appStore.collapsed" class="sidebar__status">
      <span>当前区域</span>
      <strong>{{ appStore.activeLot }}</strong>
    </div>

    <nav class="sidebar__nav">
      <RouterLink
        v-for="item in visibleMenuItems"
        :key="item.path"
        :to="item.path"
        class="sidebar__link"
        :class="{ 'sidebar__link--exact': route.path === item.path }"
      >
        <span class="sidebar__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">
            <path :d="item.icon" />
          </svg>
        </span>
        <span v-show="!appStore.collapsed">{{ item.label }}</span>
      </RouterLink>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";

import { useAppStore } from "@/store/app";
import { useUserStore } from "@/store/user";
import type { UserRole } from "@/types/domain";

type MenuItem = {
  path: string;
  label: string;
  icon: string;
  roles?: UserRole[];
};

// 侧边导航统一由数据驱动，后续新增菜单时只需要维护这一处。
const appStore = useAppStore();
const userStore = useUserStore();
const route = useRoute();

const menuItems: MenuItem[] = [
  { path: "/dashboard", label: "仪表盘", icon: "M4 13h16M7 17h10M8 6h8l1 4H7l1-4ZM6 18h12" },
  { path: "/parking/spaces", label: "车位管理", icon: "M5 9h14v10H5zM9 9V6h6v3M8 14h.01M12 14h.01M16 14h.01" },
  { path: "/records", label: "停车记录", icon: "M7 4h10M7 8h10M6 4v16h12V4M9 12h6M9 16h4" },
  { path: "/vehicles", label: "车辆管理", icon: "M5 15l1.5-4h11L19 15M7 15v3M17 15v3M8 11l1.5-3h5L16 11" },
  { path: "/users", label: "用户管理", icon: "M12 12a4 4 0 1 0 0-8a4 4 0 0 0 0 8ZM5 20a7 7 0 0 1 14 0", roles: ["admin"] },
  { path: "/detection", label: "识别测试", icon: "M4 12h16M12 4v16M7 7l10 10M17 7L7 17", roles: ["admin", "operator"] },
  { path: "/settings", label: "系统设置", icon: "M12 3v3M12 18v3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M3 12h3M18 12h3M4.9 19.1L7 17M17 7l2.1-2.1M12 15a3 3 0 1 0 0-6a3 3 0 0 0 0 6Z", roles: ["admin", "operator"] },
];

const visibleMenuItems = computed(() =>
  menuItems.filter((item) => !item.roles || item.roles.includes(userStore.role)),
);
</script>
