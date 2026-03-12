<template>
  <section class="dashboard page-stack">
    <div class="dashboard__hero panel">
      <div>
        <p class="eyebrow">{{ overview.eyebrow }}</p>
        <h1 class="dashboard__title">{{ overview.title }}</h1>
        <p class="dashboard__desc">{{ overview.description }}</p>
      </div>
      <div class="dashboard__hero-metrics">
        <div v-for="metric in overview.metrics" :key="metric.label">
          <span>{{ metric.label }}</span>
          <strong>{{ metric.value }}</strong>
        </div>
      </div>
    </div>

    <section class="page-grid page-grid--stats">
      <StatCard
        v-for="item in stats"
        :key="item.label"
        :label="item.label"
        :value="item.value"
        :trend="item.trend"
        :footnote="item.footnote"
        :type="item.type"
      />
    </section>

    <section class="dashboard__grid">
      <article class="panel page-stack">
        <div class="section-heading">
          <div>
            <h2>分区占用</h2>
            <p>按停车区查看当前空闲和占用状态。</p>
          </div>
        </div>

        <div class="space-card-grid">
          <SpaceCard
            v-for="item in dashboardSpaceBlocks"
            :key="item.title"
            :title="item.title"
            :status="item.status"
            :camera="item.camera"
            :status-type="item.statusType"
            interactive
            @click="goToSpaceList(item.title)"
          />
        </div>
      </article>

      <article class="panel page-stack">
        <div class="section-heading">
          <div>
            <h2>最近入场记录</h2>
            <p>展示最近识别到的车辆，并支持跳转到记录列表继续追踪。</p>
          </div>
        </div>

        <div class="data-list">
          <button
            v-for="record in recentRecords"
            :key="`${record.plate}-${record.time}`"
            type="button"
            class="data-list__row data-list__row--action"
            @click="goToRecordList(record.plate)"
          >
            <div class="data-list__main">
              <PlateTag :plate-number="record.plate" />
              <span>{{ record.time }}</span>
            </div>
            <span class="data-list__muted">{{ record.gate }}</span>
          </button>
        </div>
      </article>
    </section>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { getDashboardData } from "@/api/dashboard";
import PlateTag from "@/components/PlateTag.vue";
import SpaceCard from "@/components/SpaceCard.vue";
import StatCard from "@/components/StatCard.vue";
import {
  dashboardHero as dashboardHeroMock,
  dashboardRecentRecords as dashboardRecentRecordsMock,
  dashboardSpaceBlocks,
  dashboardStats as dashboardStatsMock,
} from "@/mock/dashboard";
import type { DashboardOverview, DashboardStatItem, RecentRecordItem } from "@/types/domain";

const router = useRouter();
const overview = ref<DashboardOverview>(dashboardHeroMock);
const stats = ref<DashboardStatItem[]>(dashboardStatsMock);
const recentRecords = ref<RecentRecordItem[]>(dashboardRecentRecordsMock);

function resolveZoneKeyword(title: string) {
  // 首页分区卡片只需要把区块首字母提取出来，就能把车位列表筛到对应区域。
  const match = title.match(/^([A-Z])/i);
  return match ? `${match[1].toUpperCase()} 区` : title;
}

function goToSpaceList(title: string) {
  void router.push({
    path: "/parking/spaces",
    query: {
      keyword: resolveZoneKeyword(title),
    },
  });
}

function goToRecordList(plate: string) {
  // 最近记录优先跳到记录列表并带上车牌过滤条件，避免误判详情主键。
  void router.push({
    path: "/records",
    query: {
      keyword: plate,
    },
  });
}

onMounted(async () => {
  try {
    // 优先请求后端真实数据，让首页尽早进入联调状态。
    const response = await getDashboardData();
    overview.value = response.data.overview;
    stats.value = response.data.stats;
    recentRecords.value = response.data.recent_records;
  } catch (error) {
    // 如果后端尚未启动或接口未完成，则回退到本地 mock，保证页面仍可展示。
    overview.value = dashboardHeroMock;
    stats.value = dashboardStatsMock;
    recentRecords.value = dashboardRecentRecordsMock;
  }
});
</script>
