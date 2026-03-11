<template>
  <header class="topbar">
    <button class="topbar__toggle" type="button" @click="appStore.toggleSidebar()">
      {{ appStore.collapsed ? "展开" : "收起" }}
    </button>
    <div class="topbar__title">{{ route.meta.title || appStore.title }}</div>
  </header>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";

import { useAppStore } from "@/store/app";

const appStore = useAppStore();
const route = useRoute();
</script>
