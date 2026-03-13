<template>
  <section class="page-stack">
    <article class="panel section-heading-card">
      <div>
        <h2>车辆详情</h2>
        <p>聚合车辆档案与最近停车记录，便于从记录、车辆管理和识别结果中继续追踪业务状态。</p>
      </div>
      <div class="detail-actions">
        <button type="button" class="table-action" @click="viewAllRecords">查看全部记录</button>
        <button
          type="button"
          class="table-action"
          :disabled="!detail.currentRecordId"
          @click="viewCurrentRecord"
        >
          当前在场记录
        </button>
        <button type="button" class="table-action" @click="goBack">返回车辆列表</button>
      </div>
    </article>

    <article class="detail-grid">
      <div class="panel page-stack">
        <div class="detail-item">
          <span>车牌号</span>
          <strong>{{ detail.plate }}</strong>
        </div>
        <div class="detail-item">
          <span>车主</span>
          <strong>{{ detail.owner }}</strong>
        </div>
        <div class="detail-item">
          <span>联系电话</span>
          <strong>{{ detail.ownerPhone }}</strong>
        </div>
        <div class="detail-item">
          <span>车辆类型</span>
          <strong>{{ detail.category }}</strong>
        </div>
        <div class="detail-item">
          <span>车身颜色</span>
          <strong>{{ detail.color }}</strong>
        </div>
        <div class="detail-item">
          <span>车辆状态</span>
          <strong class="status-dot status-dot--compact" :class="`status-dot--${detail.type}`">{{ detail.status }}</strong>
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
            <p>展示该车辆最近几次进出场情况，帮助快速判断当前是否在场以及历史停车习惯。</p>
          </div>
        </div>

        <div v-if="detail.recentRecords.length" class="data-list">
          <div v-for="record in detail.recentRecords" :key="record.id" class="data-list__row">
            <div class="data-list__main">
              <div>
                <strong>{{ record.recordNo }}</strong>
                <p class="data-list__muted">{{ record.enterAt }} / {{ record.leaveAt }}</p>
              </div>
            </div>
            <div class="vehicle-record-chip-group">
              <span class="status-dot" :class="`status-dot--${record.type}`">{{ record.status }}</span>
              <span class="vehicle-record-chip">¥ {{ record.amount }}</span>
              <button type="button" class="table-action" @click="viewRecordDetail(record.id)">查看记录</button>
            </div>
          </div>
        </div>
        <div v-else class="table-empty">当前车辆暂无停车记录。</div>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getVehicleDetail } from "@/api/vehicle";
import { useAppStore } from "@/store/app";
import { vehicleDetails } from "@/mock/vehicles";
import type { VehicleDetailItem } from "@/types/domain";

const route = useRoute();
const router = useRouter();
const appStore = useAppStore();

const detail = reactive<VehicleDetailItem>({
  id: 0,
  plate: "--",
  owner: "--",
  ownerPhone: "--",
  category: "--",
  color: "--",
  status: "--",
  type: "warning",
  remark: "--",
  createdAt: "--",
  updatedAt: "--",
  currentRecordId: null,
  recentRecords: [],
});

function goBack() {
  // 详情页统一返回车辆列表，保证页面切换行为可预期。
  void router.push("/vehicles");
}

function viewAllRecords() {
  // 通过车牌号跳转到停车记录页，继续追踪该车的全部停车记录。
  void router.push({
    path: "/records",
    query: {
      keyword: detail.plate === "--" ? undefined : detail.plate,
    },
  });
}

function viewCurrentRecord() {
  if (!detail.currentRecordId) {
    appStore.showMessage("当前没有在场记录", "warning");
    return;
  }
  void router.push(`/records/${detail.currentRecordId}`);
}

function viewRecordDetail(id: number) {
  void router.push(`/records/${id}`);
}

async function fetchDetail() {
  const id = Number(route.params.id);
  if (!id) {
    appStore.showMessage("车辆编号无效", "error");
    void router.push("/vehicles");
    return;
  }

  try {
    // 详情页优先读取真实接口，保证车辆档案与数据库保持一致。
    const response = await getVehicleDetail(id);
    Object.assign(detail, response.data);
  } catch (error) {
    // 联调失败时回退到本地 mock，避免详情页直接空白。
    const mockDetail = vehicleDetails.find((item) => item.id === id);
    if (!mockDetail) {
      appStore.showMessage("车辆详情获取失败", "error");
      void router.push("/vehicles");
      return;
    }

    Object.assign(detail, mockDetail);
    appStore.showMessage("车辆详情接口异常，已切换为演示数据", "warning");
  }
}

onMounted(() => {
  void fetchDetail();
});
</script>
