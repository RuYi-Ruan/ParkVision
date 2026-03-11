import { defineStore } from "pinia";
import { ref } from "vue";

export const useUserStore = defineStore("user", () => {
  const token = ref("");
  const username = ref("admin");

  function setToken(value: string) {
    token.value = value;
  }

  return {
    token,
    username,
    setToken,
  };
});
