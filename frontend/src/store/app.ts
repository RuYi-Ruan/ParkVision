import { defineStore } from "pinia";
import { computed, ref } from "vue";

type AppMessageType = "success" | "error" | "info" | "warning";

export type AppMessage = {
  id: number;
  text: string;
  type: AppMessageType;
};

export const useAppStore = defineStore("app", () => {
  // collapsed 控制侧边栏展开与收起，是布局层最核心的 UI 状态。
  const collapsed = ref(false);
  const title = ref(import.meta.env.VITE_APP_TITLE || "ParkVision");
  const activeLot = ref("主停车区 A 区");
  const messages = ref<AppMessage[]>([]);

  // 宽度使用计算属性，保证布局组件和侧边栏始终读取同一份状态。
  const sidebarWidth = computed(() => (collapsed.value ? "96px" : "268px"));

  function toggleSidebar() {
    collapsed.value = !collapsed.value;
  }

  function removeMessage(id: number) {
    messages.value = messages.value.filter((item) => item.id !== id);
  }

  function showMessage(text: string, type: AppMessageType = "info") {
    // 用时间戳和随机数组合生成 id，足够满足前端消息队列的唯一性。
    const id = Date.now() + Math.floor(Math.random() * 1000);
    messages.value.push({ id, text, type });

    window.setTimeout(() => {
      removeMessage(id);
    }, 2600);
  }

  return {
    collapsed,
    title,
    activeLot,
    sidebarWidth,
    messages,
    toggleSidebar,
    showMessage,
    removeMessage,
  };
});
