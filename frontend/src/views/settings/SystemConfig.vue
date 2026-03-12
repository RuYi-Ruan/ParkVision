<template>
  <section class="page-stack">
    <article class="panel section-heading-card">
      <div>
        <h2>系统设置</h2>
        <p>当前先搭建信息卡片式设置页，后续可接入接口参数、模型路径和系统开关。</p>
      </div>
    </article>

    <div class="settings-grid">
      <article v-for="item in systemSettings" :key="item.label" class="panel setting-card">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <p>{{ item.desc }}</p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { systemSettings } from "@/mock/settings";
</script>
