<template>
  <Teleport to="body">
    <transition name="drawer-fade">
      <div v-if="modelValue" class="drawer-mask" @click.self="handleClose">
        <aside class="drawer-panel">
          <header class="drawer-panel__head">
            <div>
              <h3>{{ title }}</h3>
              <p v-if="description">{{ description }}</p>
            </div>
            <button type="button" class="drawer-panel__close" @click="handleClose">×</button>
          </header>

          <div class="drawer-panel__body">
            <slot />
          </div>

          <footer v-if="$slots.footer" class="drawer-panel__foot">
            <slot name="footer" />
          </footer>
        </aside>
      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    modelValue: boolean;
    title: string;
    description?: string;
  }>(),
  {
    description: "",
  },
);

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
}>();

function handleClose() {
  // 抽屉关闭统一走 v-model，避免父子组件状态不同步。
  emit("update:modelValue", false);
}
</script>
