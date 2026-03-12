<template>
  <div class="upload-box" :class="{ 'upload-box--active': hasPreview }">
    <input
      ref="fileInputRef"
      class="upload-box__input"
      type="file"
      accept="image/png,image/jpeg,image/webp"
      @change="handleFileChange"
    />

    <template v-if="previewUrl">
      <div class="upload-box__preview-wrap">
        <button class="upload-box__clear" type="button" aria-label="清空图片" @click.stop="handleClear">×</button>
        <img class="upload-box__preview" :src="previewUrl" alt="上传预览" />
        <div class="upload-box__preview-badge">已加载测试图片</div>
      </div>
    </template>

    <template v-else>
      <div class="upload-box__icon">⊕</div>
      <strong>上传入口、出口或车位区域图片</strong>
      <p>支持本地 JPG / PNG / WEBP 图像，当前页面会直接生成预览并展示识别结果。</p>
    </template>

    <div class="upload-box__actions">
      <button type="button" @click="openFilePicker">选择测试图片</button>
      <span>{{ fileName || "推荐使用车牌清晰、角度稳定的测试图片" }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

const props = withDefaults(
  defineProps<{
    previewUrl?: string;
    fileName?: string;
  }>(),
  {
    previewUrl: "",
    fileName: "",
  },
);

const emit = defineEmits<{
  fileSelected: [file: File];
  clear: [];
}>();

const fileInputRef = ref<HTMLInputElement | null>(null);
const hasPreview = computed(() => Boolean(props.previewUrl));

function openFilePicker() {
  // 使用自定义按钮去触发原生 input，既保留样式自由度，也不影响上传能力。
  fileInputRef.value?.click();
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];

  if (!file) {
    return;
  }

  // 预览 URL 的创建和回收交给父组件，这里只负责把文件抛出去。
  emit("fileSelected", file);
}

function handleClear() {
  // 清空 input 的 value 后，用户才能连续选择同一张图片。
  if (fileInputRef.value) {
    fileInputRef.value.value = "";
  }

  emit("clear");
}
</script>
