<template>
  <header class="topbar">
    <div class="topbar__left">
      <button class="topbar__toggle" type="button" @click="appStore.toggleSidebar()">
        {{ appStore.collapsed ? "展开" : "收起" }}
      </button>
      <div>
        <div class="topbar__eyebrow">运营总览</div>
        <div class="topbar__title">{{ String(route.meta.title || appStore.title) }}</div>
      </div>
    </div>

    <div class="topbar__meta">
      <div class="topbar__chip">实时同步</div>
      <div class="topbar__scope">
        <span class="topbar__scope-badge">{{ userStore.roleBadge }}</span>
        <span class="topbar__scope-copy">{{ userStore.permissionSummary }}</span>
      </div>
      <div class="topbar__profile">
        <div class="topbar__avatar">管</div>
        <div class="topbar__profile-copy">
          <strong>{{ userStore.displayName }}</strong>
          <span>{{ userStore.roleName }}</span>
        </div>
      </div>
      <button class="topbar__logout" type="button" @click="handleLogout">退出</button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from "vue-router";

import { useAppStore } from "@/store/app";
import { useUserStore } from "@/store/user";

// 顶栏同时承担页面标题展示、侧边栏控制和退出登录三项职责。
const appStore = useAppStore();
const userStore = useUserStore();
const route = useRoute();
const router = useRouter();

function handleLogout() {
  // 退出后主动回到登录页，避免停留在受保护页面。
  userStore.logout();
  void router.push("/login");
}
</script>
