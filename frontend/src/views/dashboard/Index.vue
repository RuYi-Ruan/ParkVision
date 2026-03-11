<template>
  <section class="page-grid">
    <StatCard label="总车位" value="120" />
    <StatCard label="空闲车位" value="46" />
    <StatCard label="在场车辆" value="74" />
    <StatCard label="今日进场" value="218" />
  </section>
</template>

<script setup lang="ts">
import StatCard from "@/components/StatCard.vue";
</script>
