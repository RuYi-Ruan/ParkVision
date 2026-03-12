<template>
  <Teleport to="body">
    <div class="app-message-list">
      <transition-group name="message-fade">
        <div v-for="item in appStore.messages" :key="item.id" class="app-message" :class="`app-message--${item.type}`">
          <span>{{ item.text }}</span>
          <button type="button" class="app-message__close" @click="appStore.removeMessage(item.id)">×</button>
        </div>
      </transition-group>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useAppStore } from "@/store/app";

const appStore = useAppStore();
</script>
