<template>
  <aside class="sidebar" :style="{ width: appStore.sidebarWidth }">
    <div class="sidebar__brand">ParkVision</div>
    <nav class="sidebar__nav">
      <RouterLink v-for="item in menuItems" :key="item.path" :to="item.path" class="sidebar__link">
        {{ item.label }}
      </RouterLink>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { useAppStore } from "@/store/app";

const appStore = useAppStore();

const menuItems = [
  { path: "/dashboard", label: "仪表盘" },
  { path: "/parking/spaces", label: "车位管理" },
  { path: "/records", label: "停车记录" },
  { path: "/vehicles", label: "车辆管理" },
  { path: "/detection", label: "识别测试" },
  { path: "/settings", label: "系统设置" },
];
</script>
