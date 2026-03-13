<template>
  <section class="page-stack">
    <article class="panel section-heading-card">
      <div>
        <h2>记录详情</h2>
        <p>展示单条停车记录的进出场信息、费用状态和抓拍图片路径，并支持继续追踪到车辆档案页面。</p>
      </div>
      <div class="detail-actions">
        <button type="button" class="table-action" @click="viewVehicleProfile">查看车辆档案</button>
        <button type="button" class="table-action" @click="viewRelatedRecords">同车牌记录</button>
        <button type="button" class="table-action" @click="goBack">返回列表</button>
      </div>
    </article>

    <article class="panel records-rule-panel">
      <strong>费用说明</strong>
      <span>{{ detail.pricingNote }}</span>
    </article>

    <article class="detail-grid">
      <div class="panel page-stack">
        <div class="detail-item">
          <span>记录编号</span>
          <strong>{{ detail.recordNo }}</strong>
        </div>
        <div class="detail-item">
          <span>车牌号</span>
          <strong>{{ detail.plate }}</strong>
        </div>
        <div class="detail-item">
          <span>入场时间</span>
          <strong>{{ detail.enterAt }}</strong>
        </div>
        <div class="detail-item">
          <span>离场时间</span>
          <strong>{{ detail.leaveAt }}</strong>
        </div>
        <div class="detail-item">
          <span>入口通道</span>
          <strong>{{ detail.entryGate }}</strong>
        </div>
        <div class="detail-item">
          <span>出口通道</span>
          <strong>{{ detail.exitGate }}</strong>
        </div>
        <div class="detail-item">
          <span>停留时长</span>
          <strong>{{ detail.duration }}</strong>
        </div>
        <div class="detail-item">
          <span>停车费用</span>
          <strong>{{ detail.amount }} 元</strong>
        </div>
        <div class="detail-item">
          <span>支付状态</span>
          <strong>{{ detail.payStatus }}</strong>
        </div>
        <div class="detail-item">
          <span>记录状态</span>
          <strong>{{ detail.status }}</strong>
        </div>
        <div class="detail-item">
          <span>备注</span>
          <strong>{{ detail.remark }}</strong>
        </div>
      </div>

      <div class="panel page-stack">
        <div class="section-heading">
          <div>
            <h2>图片信息</h2>
            <p>当前阶段先展示图片路径，后续接入真实抓拍图后可直接替换为图片预览。</p>
          </div>
        </div>

        <div class="detail-item">
          <span>入场图片</span>
          <strong>{{ detail.entryImage || "暂无图片" }}</strong>
        </div>
        <div class="detail-item">
          <span>离场图片</span>
          <strong>{{ detail.exitImage || "暂无图片" }}</strong>
        </div>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getRecordDetail } from "@/api/record";
import { parkingRecordDetails } from "@/mock/records";
import { useAppStore } from "@/store/app";
import type { RecordDetailItem } from "@/types/domain";

const route = useRoute();
const router = useRouter();
const appStore = useAppStore();

const detail = reactive<RecordDetailItem>({
  id: 0,
  recordNo: "--",
  vehicleId: null,
  plate: "--",
  entryGate: "--",
  exitGate: "--",
  enterAt: "--",
  leaveAt: "--",
  duration: "--",
  amount: "0.00",
  payStatus: "--",
  status: "--",
  pricingNote: "当前暂无费用说明。",
  remark: "--",
  entryImage: "",
  exitImage: "",
});

function goBack() {
  // 详情页统一回到记录列表，避免浏览器历史为空时返回失败。
  void router.push("/records");
}

function viewVehicleProfile() {
  // 优先用车辆主键跳转到车辆详情；若当前记录没有绑定车辆，再回退到列表筛选。
  if (detail.vehicleId) {
    void router.push(`/vehicles/${detail.vehicleId}`);
    return;
  }

  void router.push({
    path: "/vehicles",
    query: {
      keyword: detail.plate === "--" ? undefined : detail.plate,
    },
  });
}

function viewRelatedRecords() {
  // 便于从异常记录或历史记录中继续查看同车牌的其他停车记录。
  void router.push({
    path: "/records",
    query: {
      keyword: detail.plate === "--" ? undefined : detail.plate,
    },
  });
}

async function fetchDetail() {
  const id = Number(route.params.id);
  if (!id) {
    appStore.showMessage("记录编号无效", "error");
    void router.push("/records");
    return;
  }

  try {
    // 详情页优先读取真实接口，保证字段展示与数据库保持一致。
    const response = await getRecordDetail(id);
    Object.assign(detail, response.data);
  } catch (error) {
    // 后端接口异常时，回退到本地 mock，避免演示页面直接空白。
    const mockDetail = parkingRecordDetails.find((item) => item.id === id);
    if (!mockDetail) {
      appStore.showMessage("记录详情获取失败", "error");
      void router.push("/records");
      return;
    }

    Object.assign(detail, mockDetail);
    appStore.showMessage("记录详情接口异常，已切换为演示数据。", "warning");
  }
}

onMounted(() => {
  void fetchDetail();
});
</script>
