<template>
  <span class="plate-tag">{{ plateNumber }}</span>
</template>

<script setup lang="ts">
defineProps<{
  plateNumber: string;
}>();
</script>
