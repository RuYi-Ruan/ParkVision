<template>
  <section class="page-stack">
    <article class="panel section-heading-card">
      <div>
        <h2>识别测试</h2>
        <p>上传一张测试图片，页面会展示本地预览、识别结果和检测框示意，便于后续平滑接入真实 AI 推理。</p>
      </div>
      <div class="filter-pills">
        <button
          v-for="preset in presets"
          :key="preset.id"
          type="button"
          class="filter-pill"
          :class="{ 'filter-pill--active': activePreset.id === preset.id }"
          @click="applyPreset(preset.id)"
        >
          {{ preset.label }}
        </button>
      </div>
    </article>

    <div class="detect-grid detect-grid--demo">
      <article class="panel page-stack">
        <div class="section-heading">
          <div>
            <h2>图像输入</h2>
            <p>支持本地预览。未上传时展示演示说明，上传后优先调用后端识别接口。</p>
          </div>
        </div>

        <UploadBox
          :preview-url="previewUrl"
          :file-name="selectedFileName"
          @file-selected="handleFileSelected"
          @clear="handleClearPreview"
        />
      </article>

      <article class="panel page-stack">
        <div class="section-heading">
          <div>
            <h2>识别输出</h2>
            <p>当前已接通后端识别骨架接口；若接口不可用，会自动回退到本地演示结果。</p>
          </div>
        </div>

        <div class="result-card result-card--hero" :class="{ 'result-card--flash': flashResults }">
          <span>车牌号</span>
          <strong>{{ activePreset.plate }}</strong>
        </div>

        <div class="result-grid">
          <div class="result-card" :class="{ 'result-card--flash': flashResults }">
            <span>识别类型</span>
            <strong>{{ activePreset.task }}</strong>
          </div>
          <div class="result-card" :class="{ 'result-card--flash': flashResults }">
            <span>置信度</span>
            <strong>{{ activePreset.confidence }}</strong>
          </div>
          <div class="result-card" :class="{ 'result-card--flash': flashResults }">
            <span>车辆类型</span>
            <strong>{{ activePreset.vehicleType }}</strong>
          </div>
          <div class="result-card" :class="{ 'result-card--flash': flashResults }">
            <span>位置区域</span>
            <strong>{{ activePreset.location }}</strong>
          </div>
        </div>

        <div class="detect-timeline">
          <div v-for="item in activePreset.steps" :key="item.label" class="detect-timeline__item">
            <strong>{{ item.label }}</strong>
            <span>{{ item.value }}</span>
          </div>
        </div>
      </article>
    </div>

    <article ref="previewSectionRef" class="panel page-stack">
      <div class="section-heading">
        <div>
          <h2>检测框示意</h2>
          <p>用于模拟车牌或车辆检测结果在图像上的落点区域。</p>
        </div>
      </div>

      <div class="detect-preview">
        <template v-if="previewUrl">
          <img class="detect-preview__image" :src="previewUrl" alt="检测预览" />
          <div class="detect-preview__box" :style="activePreset.boxStyle">
            <span>{{ activePreset.plate }}</span>
          </div>
        </template>
        <template v-else>
          <div class="detect-preview__placeholder">
            <strong>等待上传测试图片</strong>
            <span>选择上方图片后，这里会叠加模拟检测框。</span>
          </div>
        </template>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";

import { detectImage, getDetectPresets } from "@/api/detect";
import UploadBox from "@/components/UploadBox.vue";
import { detectPresets as detectPresetsMock } from "@/mock/detection";
import type { DetectResult } from "@/types/domain";

const presets = ref<DetectResult[]>(detectPresetsMock);
const activePresetId = ref("entry");
const previewUrl = ref("");
const selectedFileName = ref("");
const flashResults = ref(false);
const previewSectionRef = ref<HTMLElement | null>(null);
let flashTimer: number | null = null;

// 当前选中的结果同时控制结果卡片内容和检测框位置。
const activePreset = computed(() => presets.value.find((item) => item.id === activePresetId.value) ?? presets.value[0]);

async function loadPresets() {
  try {
    const response = await getDetectPresets();
    presets.value = response.data.length ? response.data : detectPresetsMock;
  } catch (error) {
    presets.value = detectPresetsMock;
  }
}

function applyPreset(id: string) {
  activePresetId.value = id;
}

async function handleFileSelected(file: File) {
  // 切换图片前先释放旧的对象 URL，避免重复上传导致内存浪费。
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }

  previewUrl.value = URL.createObjectURL(file);
  selectedFileName.value = file.name;

  const formData = new FormData();
  formData.append("image", file);
  formData.append("preset_id", activePresetId.value);

  try {
    // 优先调用后端识别骨架接口，让上传流程尽早进入真实联调状态。
    const response = await detectImage(formData);
    upsertPreset(response.data);
    activePresetId.value = response.data.id;
  } catch (error) {
    // 如果后端未启动或接口不可用，则保留当前本地预设结果。
  }

  triggerPreviewFocus();
}

function upsertPreset(result: DetectResult) {
  const index = presets.value.findIndex((item) => item.id === result.id);
  if (index >= 0) {
    presets.value[index] = result;
    presets.value = [...presets.value];
    return;
  }

  presets.value = [...presets.value, result];
}

function handleClearPreview() {
  // 清空后回到初始演示状态，便于用户重新测试其它图片。
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }

  previewUrl.value = "";
  selectedFileName.value = "";
}

function triggerPreviewFocus() {
  // 高亮结果卡片并滚动到预览区域，让上传后的反馈更直接。
  flashResults.value = true;

  if (flashTimer) {
    window.clearTimeout(flashTimer);
  }

  flashTimer = window.setTimeout(() => {
    flashResults.value = false;
  }, 1400);

  void nextTick(() => {
    // 等 DOM 完成更新后再滚动，避免定位到旧布局位置。
    previewSectionRef.value?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  });
}

onMounted(() => {
  void loadPresets();
});

onBeforeUnmount(() => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }

  if (flashTimer) {
    window.clearTimeout(flashTimer);
  }
});
</script>
