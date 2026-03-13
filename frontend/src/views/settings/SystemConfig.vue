<template>
  <section class="page-stack">
    <article class="panel section-heading-card">
      <div>
        <h2>系统设置</h2>
        <p>统一维护停车收费规则、识别参数和系统运行配置，后续接入 YOLO 后可直接复用本页作为参数管理入口。</p>
      </div>
      <div class="detail-actions">
        <span class="settings-updated-at">最近保存：{{ form.updated_at || "未保存" }}</span>
        <button
          v-if="userStore.canEditSystemConfig"
          type="button"
          class="table-action table-action--primary"
          @click="handleSubmit"
        >
          保存设置
        </button>
      </div>
    </article>

    <article v-if="!userStore.canEditSystemConfig" class="panel">
      <p class="manage-panel__error">当前账号仅可查看系统设置，修改权限仅对系统管理员开放。</p>
    </article>

    <section class="settings-grid settings-grid--config">
      <article class="panel settings-section">
        <div class="section-heading">
          <div>
            <h2>停车收费规则</h2>
            <p>用于入口、出口和停车记录的收费计算，可作为后续业务规则配置的基础。</p>
          </div>
        </div>

        <div class="manage-form">
          <label>
            <span>免费时长（分钟）</span>
            <input v-model.number="form.parking_rule.free_minutes" :disabled="!userStore.canEditSystemConfig" type="number" min="0" />
          </label>
          <label>
            <span>每小时收费（元）</span>
            <input v-model="form.parking_rule.fee_per_hour" :disabled="!userStore.canEditSystemConfig" type="text" />
          </label>
          <label>
            <span>单日封顶（元）</span>
            <input v-model="form.parking_rule.daily_cap" :disabled="!userStore.canEditSystemConfig" type="text" />
          </label>
          <label>
            <span>超时阈值（小时）</span>
            <input v-model.number="form.parking_rule.overdue_hours" :disabled="!userStore.canEditSystemConfig" type="number" min="1" />
          </label>
        </div>
      </article>

      <article class="panel settings-section">
        <div class="section-heading">
          <div>
            <h2>识别参数</h2>
            <p>当前先作为配置骨架保存，后续接入模型推理后可直接作为阈值和模型路径来源。</p>
          </div>
        </div>

        <div class="manage-form">
          <label>
            <span>检测置信度阈值</span>
            <input v-model="form.recognition.detect_confidence" :disabled="!userStore.canEditSystemConfig" type="text" />
          </label>
          <label>
            <span>OCR 置信度阈值</span>
            <input v-model="form.recognition.ocr_confidence" :disabled="!userStore.canEditSystemConfig" type="text" />
          </label>
          <label class="manage-form__wide">
            <span>车辆模型路径</span>
            <input v-model="form.recognition.yolo_model_path" :disabled="!userStore.canEditSystemConfig" type="text" />
          </label>
          <label class="manage-form__wide">
            <span>车牌模型路径</span>
            <input v-model="form.recognition.plate_model_path" :disabled="!userStore.canEditSystemConfig" type="text" />
          </label>
        </div>
      </article>

      <article class="panel settings-section">
        <div class="section-heading">
          <div>
            <h2>系统运行配置</h2>
            <p>控制首页默认区域、监控刷新频率以及记录保留策略，方便后续部署与演示。</p>
          </div>
        </div>

        <div class="manage-form">
          <label class="manage-form__wide">
            <span>默认区域</span>
            <input v-model="form.runtime.default_zone" :disabled="!userStore.canEditSystemConfig" type="text" />
          </label>
          <label>
            <span>监控刷新间隔（秒）</span>
            <input
              v-model.number="form.runtime.monitor_refresh_seconds"
              :disabled="!userStore.canEditSystemConfig"
              type="number"
              min="5"
            />
          </label>
          <label>
            <span>自动导出周期（天）</span>
            <input v-model.number="form.runtime.auto_export_days" :disabled="!userStore.canEditSystemConfig" type="number" min="1" />
          </label>
          <label>
            <span>记录保留天数</span>
            <input v-model.number="form.runtime.retain_days" :disabled="!userStore.canEditSystemConfig" type="number" min="1" />
          </label>
        </div>
      </article>
    </section>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive } from "vue";

import { getSystemConfig, updateSystemConfig } from "@/api/settings";
import { systemConfigMock } from "@/mock/settings";
import { useAppStore } from "@/store/app";
import { useUserStore } from "@/store/user";
import type { SystemConfigData } from "@/types/domain";

const appStore = useAppStore();
const userStore = useUserStore();

const form = reactive<SystemConfigData>({
  parking_rule: {
    free_minutes: 15,
    fee_per_hour: "6.00",
    daily_cap: "48.00",
    overdue_hours: 24,
  },
  recognition: {
    detect_confidence: "0.45",
    ocr_confidence: "0.60",
    yolo_model_path: "",
    plate_model_path: "",
  },
  runtime: {
    default_zone: "",
    monitor_refresh_seconds: 30,
    auto_export_days: 30,
    retain_days: 365,
  },
  updated_at: "",
});

function fillConfig(data: SystemConfigData) {
  // 统一使用 Object.assign 填充三组配置，避免逐字段重复赋值。
  Object.assign(form.parking_rule, data.parking_rule);
  Object.assign(form.recognition, data.recognition);
  Object.assign(form.runtime, data.runtime);
  form.updated_at = data.updated_at || "";
}

async function fetchConfig() {
  try {
    const response = await getSystemConfig();
    fillConfig(response.data);
  } catch (error) {
    // 如果后端尚未启动或接口异常，则回退到本地默认配置，保证页面可查看。
    fillConfig(systemConfigMock);
    appStore.showMessage("系统设置接口异常，已切换为演示配置。", "warning");
  }
}

async function handleSubmit() {
  if (!userStore.canEditSystemConfig) {
    appStore.showMessage("当前账号没有修改系统设置的权限。", "warning");
    return;
  }

  try {
    const payload = {
      parking_rule: { ...form.parking_rule },
      recognition: { ...form.recognition },
      runtime: { ...form.runtime },
    };
    const response = await updateSystemConfig(payload);
    fillConfig(response.data);
    appStore.showMessage("系统设置已保存。", "success");
  } catch (error: any) {
    const message = error?.response?.data?.message || "系统设置保存失败，请稍后重试。";
    appStore.showMessage(message, "error");
  }
}

onMounted(() => {
  void fetchConfig();
});
</script>
