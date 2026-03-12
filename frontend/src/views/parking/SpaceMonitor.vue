<template>
  <section class="page-stack">
    <article class="panel section-heading-card">
      <div>
        <h2>车位监控</h2>
        <p>模拟车位监控大屏的实时卡片视图，并支持跳转到对应的车位列表筛选结果。</p>
      </div>
    </article>

    <div class="monitor-grid">
      <button
        v-for="block in monitorBlocks"
        :key="block.name"
        type="button"
        class="panel monitor-block monitor-block--action"
        @click="goToSpaceList(block.name)"
      >
        <div class="monitor-block__head">
          <strong>{{ block.name }}</strong>
          <span>{{ block.camera }}</span>
        </div>
        <div class="monitor-block__chart">
          <div class="monitor-block__fill" :style="{ width: block.rate }"></div>
        </div>
        <div class="monitor-block__foot">
          <span>占用率</span>
          <strong>{{ block.rate }}</strong>
        </div>
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { getParkingMonitor } from "@/api/parking";
import { parkingMonitorBlocks } from "@/mock/parking";
import type { ParkingMonitorItem } from "@/types/domain";

const router = useRouter();
const monitorBlocks = ref<ParkingMonitorItem[]>(parkingMonitorBlocks);

function resolveZoneKeyword(name: string) {
  // 监控块名称通常带“视角”等后缀，这里优先提取区域关键词给列表页使用。
  const letterMatch = name.match(/([A-Z])/i);
  if (letterMatch) {
    return `${letterMatch[1].toUpperCase()} 区`;
  }

  if (name.includes("地下")) {
    return "地下";
  }

  return name.replace(/视角/g, "");
}

function goToSpaceList(name: string) {
  void router.push({
    path: "/parking/spaces",
    query: {
      keyword: resolveZoneKeyword(name),
    },
  });
}

onMounted(async () => {
  try {
    // 监控页优先读取真实接口，方便后续继续扩展区域占用统计。
    const response = await getParkingMonitor();
    monitorBlocks.value = response.data;
  } catch (error) {
    // 接口异常时仍展示本地监控块，保证监控页可演示。
    monitorBlocks.value = parkingMonitorBlocks;
  }
});
</script>
