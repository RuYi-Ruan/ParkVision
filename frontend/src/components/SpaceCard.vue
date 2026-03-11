<template>
  <div class="panel">
    <div>{{ title }}</div>
    <strong>{{ status }}</strong>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  status: string;
}>();
</script>
