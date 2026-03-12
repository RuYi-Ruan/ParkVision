<template>
  <component :is="interactive ? 'button' : 'article'" class="space-card panel" :class="{ 'space-card--action': interactive }">
    <div class="space-card__head">
      <span class="space-card__title">{{ title }}</span>
      <span class="space-card__status" :class="`space-card__status--${statusType}`">{{ status }}</span>
    </div>
    <div class="space-card__meta">摄像头 {{ camera }}</div>
  </component>
</template>

<script setup lang="ts">
// 车位概览卡片只负责展示单个区域块，不在组件内部承担业务逻辑。
// 当 interactive 为 true 时，根节点会退化为 button，便于承接外部跳转行为。
withDefaults(
  defineProps<{
    title: string;
    status: string;
    camera?: string;
    statusType?: "free" | "busy" | "warning";
    interactive?: boolean;
  }>(),
  {
    camera: "01",
    statusType: "free",
    interactive: false,
  },
);
</script>
