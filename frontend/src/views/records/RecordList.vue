<template>
  <section class="page-stack">
    <article class="panel section-heading-card">
      <div>
        <h2>停车记录</h2>
        <p>用于展示车辆进出场、停留时长和当前状态，并支持跳转查看单条记录详情。</p>
      </div>
      <div class="filter-pills">
        <button
          v-for="item in recordStatusFilters"
          :key="item.value"
          type="button"
          class="filter-pill"
          :class="{ 'filter-pill--active': activeStatus === item.value }"
          @click="activeStatus = item.value"
        >
          {{ item.label }}
        </button>
      </div>
    </article>

    <article class="panel toolbar-panel">
      <input v-model.trim="keyword" class="toolbar-search" type="text" placeholder="搜索车牌号、记录编号或状态" />
      <div class="toolbar-summary">共筛选出 {{ filteredRecords.length }} 条记录</div>
    </article>

    <article class="panel table-panel">
      <div class="table-header table-header--records table-header--manage">
        <span>车牌号</span>
        <span>入场时间</span>
        <span>离场时间</span>
        <span>停留时长</span>
        <span>状态</span>
        <span>操作</span>
      </div>
      <div v-for="record in filteredRecords" :key="record.id" class="table-row table-row--records table-row--manage">
        <strong>{{ record.plate }}</strong>
        <span>{{ record.enterAt }}</span>
        <span>{{ record.leaveAt }}</span>
        <span>{{ record.duration }}</span>
        <span class="status-dot" :class="`status-dot--${record.type}`">{{ record.status }}</span>
        <button type="button" class="table-action" @click="goDetail(record.id)">查看详情</button>
      </div>
      <div v-if="!filteredRecords.length" class="table-empty">没有符合条件的停车记录。</div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";

import { getRecordList } from "@/api/record";
import { parkingRecords as parkingRecordsMock, recordStatusFilters } from "@/mock/records";
import type { RecordItem } from "@/types/domain";

type RecordStatus = "all" | "busy" | "free" | "warning";

const router = useRouter();
const keyword = ref("");
const activeStatus = ref<RecordStatus>("all");
const records = ref<RecordItem[]>(parkingRecordsMock);

const filteredRecords = computed(() => {
  // 即使后端已支持筛选，前端仍保留同构过滤逻辑，以兼容 mock 回退场景。
  return records.value.filter((record) => {
    const matchStatus = activeStatus.value === "all" || record.type === activeStatus.value;
    const matchKeyword =
      !keyword.value ||
      `${record.plate}${record.enterAt}${record.leaveAt}${record.status}${record.recordNo}`
        .toLowerCase()
        .includes(keyword.value.toLowerCase());

    return matchStatus && matchKeyword;
  });
});

function goDetail(id: number) {
  // 详情页按主键跳转，便于后端直接查询单条记录。
  void router.push(`/records/${id}`);
}

async function fetchRecords() {
  try {
    // 将工具栏的筛选状态映射为接口参数，保证页面表现与请求条件一致。
    const response = await getRecordList({
      keyword: keyword.value || undefined,
      status: activeStatus.value === "all" ? undefined : activeStatus.value,
    });
    records.value = response.data;
  } catch (error) {
    // 联调失败时回退到本地数据，避免演示页面直接空白。
    records.value = parkingRecordsMock;
  }
}

watch([keyword, activeStatus], () => {
  void fetchRecords();
});

onMounted(() => {
  void fetchRecords();
});
</script>
