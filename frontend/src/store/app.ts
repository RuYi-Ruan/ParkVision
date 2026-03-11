import { defineStore } from "pinia";
import { computed, ref } from "vue";

export const useAppStore = defineStore("app", () => {
  const collapsed = ref(false);
  const title = ref(import.meta.env.VITE_APP_TITLE || "ParkVision");

  const sidebarWidth = computed(() => (collapsed.value ? "84px" : "260px"));

  function toggleSidebar() {
    collapsed.value = !collapsed.value;
  }

  return {
    collapsed,
    title,
    sidebarWidth,
    toggleSidebar,
  };
});
