<template>
  <section class="page-stack">
    <article class="panel section-heading-card">
      <div>
        <h2>车位详情</h2>
        <p>聚合车位档案与最近停车记录，便于从车位监控、车位列表和停车记录中继续追踪当前占用情况。</p>
      </div>
      <div class="detail-actions">
        <button type="button" class="table-action" :disabled="!detail.currentRecordId" @click="viewCurrentRecord">
          当前占用记录
        </button>
        <button type="button" class="table-action" :disabled="detail.currentPlate === '--'" @click="viewCurrentVehicle">
          当前占用车辆
        </button>
        <button type="button" class="table-action" @click="goBack">返回车位列表</button>
      </div>
    </article>

    <article class="detail-grid">
      <div class="panel page-stack">
        <div class="detail-item">
          <span>车位编号</span>
          <strong>{{ detail.code }}</strong>
        </div>
        <div class="detail-item">
          <span>所属区域</span>
          <strong>{{ detail.zone }}</strong>
        </div>
        <div class="detail-item">
          <span>车位类型</span>
          <strong>{{ detail.spaceType }}</strong>
        </div>
        <div class="detail-item">
          <span>当前状态</span>
          <strong class="status-dot status-dot--compact" :class="`status-dot--${detail.type}`">{{ detail.status }}</strong>
        </div>
        <div class="detail-item">
          <span>楼层</span>
          <strong>{{ detail.floorNo }}</strong>
        </div>
        <div class="detail-item">
          <span>当前车牌</span>
          <strong>{{ detail.currentPlate }}</strong>
        </div>
        <div class="detail-item">
          <span>备注</span>
          <strong>{{ detail.remark }}</strong>
        </div>
        <div class="detail-item">
          <span>创建时间</span>
          <strong>{{ detail.createdAt }}</strong>
        </div>
        <div class="detail-item">
          <span>更新时间</span>
          <strong>{{ detail.updatedAt }}</strong>
        </div>
      </div>

      <div class="panel page-stack">
        <div class="section-heading">
          <div>
            <h2>最近停车记录</h2>
            <p>展示该车位最近几次停车情况，便于快速判断该位置是否高频占用、是否存在异常记录。</p>
          </div>
        </div>

        <div v-if="detail.recentRecords.length" class="data-list">
          <div v-for="record in detail.recentRecords" :key="record.id" class="data-list__row">
            <div class="data-list__main">
              <div>
                <strong>{{ record.recordNo }}</strong>
                <p class="data-list__muted">{{ record.plate }} / {{ record.enterAt }}</p>
              </div>
            </div>
            <div class="vehicle-record-chip-group">
              <span class="status-dot" :class="`status-dot--${record.type}`">{{ record.status }}</span>
              <span class="vehicle-record-chip">¥ {{ record.amount }}</span>
              <button type="button" class="table-action" @click="viewRecordDetail(record.id)">查看记录</button>
            </div>
          </div>
        </div>
        <div v-else class="table-empty">当前车位暂无停车记录。</div>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getParkingSpaceDetail } from "@/api/parking";
import { parkingSpaceDetails } from "@/mock/parking";
import { useAppStore } from "@/store/app";
import type { ParkingSpaceDetailItem } from "@/types/domain";

const route = useRoute();
const router = useRouter();
const appStore = useAppStore();

const detail = reactive<ParkingSpaceDetailItem>({
  id: 0,
  code: "--",
  zone: "--",
  spaceType: "--",
  status: "--",
  type: "warning",
  floorNo: "--",
  remark: "--",
  createdAt: "--",
  updatedAt: "--",
  currentPlate: "--",
  currentRecordId: null,
  recentRecords: [],
});

function goBack() {
  // 详情页统一返回车位列表，保证页面切换行为可预期。
  void router.push("/parking/spaces");
}

function viewCurrentRecord() {
  if (!detail.currentRecordId) {
    appStore.showMessage("当前没有占用记录", "warning");
    return;
  }
  void router.push(`/records/${detail.currentRecordId}`);
}

function viewCurrentVehicle() {
  if (detail.currentPlate === "--") {
    appStore.showMessage("当前车位没有占用车辆", "warning");
    return;
  }
  void router.push({
    path: "/vehicles",
    query: {
      keyword: detail.currentPlate,
    },
  });
}

function viewRecordDetail(id: number) {
  void router.push(`/records/${id}`);
}

async function fetchDetail() {
  const id = Number(route.params.id);
  if (!id) {
    appStore.showMessage("车位编号无效", "error");
    void router.push("/parking/spaces");
    return;
  }

  try {
    // 详情页优先读取真实接口，保证车位档案与数据库保持一致。
    const response = await getParkingSpaceDetail(id);
    Object.assign(detail, response.data);
  } catch (error) {
    // 联调失败时回退到本地 mock，避免详情页直接空白。
    const mockDetail = parkingSpaceDetails.find((item) => item.id === id);
    if (!mockDetail) {
      appStore.showMessage("车位详情获取失败", "error");
      void router.push("/parking/spaces");
      return;
    }

    Object.assign(detail, mockDetail);
    appStore.showMessage("车位详情接口异常，已切换为演示数据", "warning");
  }
}

onMounted(() => {
  void fetchDetail();
});
</script>
