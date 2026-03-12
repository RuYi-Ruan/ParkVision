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
      <span>当前园区</span>
      <strong>{{ appStore.activeLot }}</strong>
    </div>

    <nav class="sidebar__nav">
      <RouterLink
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="sidebar__link"
        :class="{ 'sidebar__link--exact': route.path === item.path }"
      >
        <span class="sidebar__icon">{{ item.icon }}</span>
        <span v-show="!appStore.collapsed">{{ item.label }}</span>
      </RouterLink>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";

import { useAppStore } from "@/store/app";

// 侧边导航统一由数据驱动，后续新增菜单时只需要维护这一处。
const appStore = useAppStore();
const route = useRoute();

const menuItems = [
  { path: "/dashboard", label: "仪表盘", icon: "◫" },
  { path: "/parking/spaces", label: "车位管理", icon: "◧" },
  { path: "/records", label: "停车记录", icon: "◎" },
  { path: "/vehicles", label: "车辆管理", icon: "▣" },
  { path: "/detection", label: "识别测试", icon: "◉" },
  { path: "/settings", label: "系统设置", icon: "⚙" },
];
</script>
