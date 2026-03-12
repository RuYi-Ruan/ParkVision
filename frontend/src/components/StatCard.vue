<template>
  <article class="stat-card panel">
    <div class="stat-card__label-row">
      <span class="stat-card__label">{{ label }}</span>
      <span class="stat-card__trend" :class="trendClass">{{ trend }}</span>
    </div>
    <div class="stat-card__value">{{ value }}</div>
    <div class="stat-card__foot">{{ footnote }}</div>
  </article>
</template>

<script setup lang="ts">
import { computed } from "vue";

// 统计卡片是一个纯展示组件，通过 props 统一承接首页上的统计数据。
const props = withDefaults(
  defineProps<{
    label: string;
    value: string | number;
    trend?: string;
    footnote?: string;
    type?: "positive" | "neutral" | "warning";
  }>(),
  {
    trend: "平稳",
    footnote: "较昨日数据对比",
    type: "neutral",
  },
);

// 趋势颜色由 type 决定，避免模板里拼接过多展示逻辑。
const trendClass = computed(() => `stat-card__trend--${props.type}`);
</script>
