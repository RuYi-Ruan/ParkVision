<template>
  <section class="page-stack">
    <article class="panel section-heading-card">
      <div>
        <h2>停车记录</h2>
        <p>
          统一查看车辆入场、离场、停留时长与收费状态。当前页面支持按关键词、记录状态、支付状态和入场日期筛选，
          同时也提供模拟入场、模拟出场和导出能力，方便在未接入 YOLO 前先验证业务闭环。
        </p>
      </div>
      <div class="manage-panel__actions">
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
        <div v-if="canManageRecords" class="manage-panel__actions">
          <button type="button" class="table-action" @click="openEntryDrawer">模拟入场</button>
          <button type="button" class="table-action table-action--primary" @click="openExitDrawer">模拟出场</button>
        </div>
      </div>
    </article>

    <section class="records-summary-grid">
      <article class="panel records-summary-card">
        <span class="records-summary-card__label">记录总数</span>
        <strong class="records-summary-card__value">{{ summary.totalCount }}</strong>
        <span class="records-summary-card__foot">当前筛选条件下的全部停车记录</span>
      </article>
      <article class="panel records-summary-card">
        <span class="records-summary-card__label">当前在场</span>
        <strong class="records-summary-card__value">{{ summary.inLotCount }}</strong>
        <span class="records-summary-card__foot">仍未完成出场闭环的记录数量</span>
      </article>
      <article class="panel records-summary-card">
        <span class="records-summary-card__label">超时在场</span>
        <strong class="records-summary-card__value">{{ summary.overdueCount }}</strong>
        <span class="records-summary-card__foot">超过系统阈值后仍未离场的记录数量</span>
      </article>
      <article class="panel records-summary-card">
        <span class="records-summary-card__label">已收金额</span>
        <strong class="records-summary-card__value">¥ {{ summary.totalAmount }}</strong>
        <span class="records-summary-card__foot">当前筛选范围内已支付记录的累计金额</span>
      </article>
    </section>

    <article class="panel records-rule-panel">
      <strong>计费规则</strong>
      <span>{{ summary.ruleSummary }}</span>
      <em>待支付记录：{{ summary.unpaidCount }} 条</em>
    </article>

    <article class="panel toolbar-panel toolbar-panel--records">
      <div class="records-filter-grid">
        <div class="toolbar-field">
          <span class="toolbar-field__label">关键词</span>
          <input
            v-model.trim="keyword"
            class="toolbar-search"
            type="text"
            placeholder="搜索车牌号、记录编号或状态"
          />
        </div>
        <div class="toolbar-field">
          <span class="toolbar-field__label">支付状态</span>
          <select v-model="payStatus" class="toolbar-select">
            <option v-for="item in recordPayStatusFilters" :key="item.value" :value="item.value">
              {{ item.label }}
            </option>
          </select>
        </div>
        <div class="toolbar-field">
          <span class="toolbar-field__label">开始日期</span>
          <input v-model="dateFrom" class="toolbar-search toolbar-search--date" type="date" />
        </div>
        <div class="toolbar-field">
          <span class="toolbar-field__label">结束日期</span>
          <input v-model="dateTo" class="toolbar-search toolbar-search--date" type="date" />
        </div>
      </div>
      <div class="toolbar-actions">
        <div class="toolbar-summary toolbar-summary--records">共筛选出 {{ filteredRecords.length }} 条记录</div>
        <button
          v-if="canExportRecords"
          type="button"
          class="table-action table-action--primary"
          @click="handleExport"
        >
          导出 CSV
        </button>
      </div>
    </article>

    <article v-if="!canManageRecords || !canExportRecords" class="panel">
      <p class="manage-panel__error">
        {{ permissionHint }}
      </p>
    </article>

    <article class="panel table-panel">
      <div class="table-header table-header--records-extended">
        <span>车牌号</span>
        <span>入场时间</span>
        <span>离场时间</span>
        <span>停留时长</span>
        <span>停车费用</span>
        <span>支付状态</span>
        <span>记录状态</span>
        <span>操作</span>
      </div>
      <div v-for="record in filteredRecords" :key="record.id" class="table-row table-row--records-extended">
        <strong>{{ record.plate }}</strong>
        <span>{{ record.enterAt }}</span>
        <span>{{ record.leaveAt }}</span>
        <span>{{ record.duration }}</span>
        <span>¥ {{ record.amount }}</span>
        <span class="status-dot" :class="record.payStatus === '已支付' ? 'status-dot--free' : 'status-dot--busy'">
          {{ record.payStatus }}
        </span>
        <span class="status-dot" :class="`status-dot--${record.type}`">{{ record.status }}</span>
        <button type="button" class="table-action" @click="goDetail(record.id)">查看详情</button>
      </div>
      <div v-if="!filteredRecords.length" class="table-empty">没有符合条件的停车记录。</div>
    </article>

    <RightDrawer
      v-if="canManageRecords"
      v-model="entryDrawerVisible"
      title="模拟车辆入场"
      description="手动输入车牌和入口信息，系统会自动创建停车记录并优先占用所选或首个空闲车位。"
    >
      <div class="manage-form">
        <label>
          <span>车牌号</span>
          <input
            v-model.trim="entryForm.plate_number"
            :class="{ 'manage-form__input--error': Boolean(entryErrors.plate_number) }"
            type="text"
            placeholder="例如：粤B·A2138"
          />
          <small v-if="entryErrors.plate_number" class="manage-form__field-error">{{ entryErrors.plate_number }}</small>
        </label>
        <label>
          <span>入口通道</span>
          <input
            v-model.trim="entryForm.entry_gate"
            :class="{ 'manage-form__input--error': Boolean(entryErrors.entry_gate) }"
            type="text"
            placeholder="例如：东入口"
          />
          <small v-if="entryErrors.entry_gate" class="manage-form__field-error">{{ entryErrors.entry_gate }}</small>
        </label>
        <label>
          <span>分配车位</span>
          <select v-model="entryForm.space_id">
            <option value="">自动分配空闲车位</option>
            <option v-for="space in freeSpaceOptions" :key="space.id" :value="String(space.id)">
              {{ space.code }} · {{ space.zone }}
            </option>
          </select>
        </label>
        <label class="manage-form__wide">
          <span>备注</span>
          <input v-model.trim="entryForm.remark" type="text" placeholder="可选填写，例如访客车辆或演示入场" />
        </label>
      </div>

      <p v-if="entryFormError" class="manage-panel__error">{{ entryFormError }}</p>

      <template #footer>
        <button type="button" class="table-action" @click="closeEntryDrawer">取消</button>
        <button type="button" class="table-action table-action--primary" @click="handleEntrySubmit">确认入场</button>
      </template>
    </RightDrawer>

    <RightDrawer
      v-if="canManageRecords"
      v-model="exitDrawerVisible"
      title="模拟车辆出场"
      description="根据车牌查找当前在场记录，并按系统设置中的收费规则完成结算与车位释放。"
    >
      <div class="manage-form">
        <label>
          <span>车牌号</span>
          <input
            v-model.trim="exitForm.plate_number"
            :class="{ 'manage-form__input--error': Boolean(exitErrors.plate_number) }"
            type="text"
            placeholder="请输入在场车辆车牌号"
          />
          <small v-if="exitErrors.plate_number" class="manage-form__field-error">{{ exitErrors.plate_number }}</small>
        </label>
        <label>
          <span>出口通道</span>
          <input
            v-model.trim="exitForm.exit_gate"
            :class="{ 'manage-form__input--error': Boolean(exitErrors.exit_gate) }"
            type="text"
            placeholder="例如：南出口"
          />
          <small v-if="exitErrors.exit_gate" class="manage-form__field-error">{{ exitErrors.exit_gate }}</small>
        </label>
        <label class="manage-form__wide">
          <span>备注</span>
          <input v-model.trim="exitForm.remark" type="text" placeholder="可选填写，例如人工放行或演示结算" />
        </label>
      </div>

      <p v-if="exitFormError" class="manage-panel__error">{{ exitFormError }}</p>

      <template #footer>
        <button type="button" class="table-action" @click="closeExitDrawer">取消</button>
        <button type="button" class="table-action table-action--primary" @click="handleExitSubmit">确认出场</button>
      </template>
    </RightDrawer>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getParkingSpaces } from "@/api/parking";
import {
  createEntryRecord,
  exportRecordList,
  getRecordList,
  getRecordSummary,
  settleExitRecord,
  type RecordEntryFormData,
  type RecordExitFormData,
} from "@/api/record";
import RightDrawer from "@/components/RightDrawer.vue";
import { parkingRecords as parkingRecordsMock, recordPayStatusFilters, recordStatusFilters } from "@/mock/records";
import { useAppStore } from "@/store/app";
import { useUserStore } from "@/store/user";
import type { ParkingSpaceItem, RecordItem, RecordSummary } from "@/types/domain";

type RecordStatus = "all" | "busy" | "free" | "warning";
type EntryFormErrors = Record<"plate_number" | "entry_gate", string>;
type ExitFormErrors = Record<"plate_number" | "exit_gate", string>;
type EntryFormState = {
  plate_number: string;
  entry_gate: string;
  space_id: string;
  remark: string;
};
type ExitFormState = {
  plate_number: string;
  exit_gate: string;
  remark: string;
};

const route = useRoute();
const router = useRouter();
const appStore = useAppStore();
const userStore = useUserStore();

// 将筛选项与路由参数绑定，便于从其他页面跳转过来时直接带条件查看。
const keyword = ref(typeof route.query.keyword === "string" ? route.query.keyword : "");
const activeStatus = ref<RecordStatus>(
  route.query.status === "busy" || route.query.status === "free" || route.query.status === "warning"
    ? route.query.status
    : "all",
);
const payStatus = ref(typeof route.query.payStatus === "string" ? route.query.payStatus : "all");
const dateFrom = ref(typeof route.query.dateFrom === "string" ? route.query.dateFrom : "");
const dateTo = ref(typeof route.query.dateTo === "string" ? route.query.dateTo : "");

const records = ref<RecordItem[]>(parkingRecordsMock);
const freeSpaceOptions = ref<ParkingSpaceItem[]>([]);
const entryDrawerVisible = ref(false);
const exitDrawerVisible = ref(false);
const entryFormError = ref("");
const exitFormError = ref("");

const entryForm = reactive<EntryFormState>({
  plate_number: "",
  entry_gate: "",
  space_id: "",
  remark: "",
});
const exitForm = reactive<ExitFormState>({
  plate_number: "",
  exit_gate: "",
  remark: "",
});

const entryErrors = reactive<EntryFormErrors>({
  plate_number: "",
  entry_gate: "",
});
const exitErrors = reactive<ExitFormErrors>({
  plate_number: "",
  exit_gate: "",
});

const summary = reactive<RecordSummary>({
  totalCount: parkingRecordsMock.length,
  inLotCount: parkingRecordsMock.filter((item) => item.status === "在场" || item.status === "超时在场").length,
  departedCount: parkingRecordsMock.filter((item) => item.status === "已离场").length,
  unpaidCount: parkingRecordsMock.filter((item) => item.payStatus === "未支付").length,
  overdueCount: parkingRecordsMock.filter((item) => item.status === "超时在场").length,
  totalAmount: parkingRecordsMock
    .filter((item) => item.payStatus === "已支付")
    .reduce((total, item) => total + Number(item.amount), 0)
    .toFixed(2),
  ruleSummary: "当前使用演示收费规则：免费 15 分钟，超出后按 6.00 元/小时向上计费，单日封顶 48.00 元。",
});

const filteredRecords = computed(() => {
  // 即使后端已经支持筛选，前端仍保留一层同构过滤，确保 mock 回退时体验一致。
  return records.value.filter((record) => {
    const matchStatus = activeStatus.value === "all" || record.type === activeStatus.value;
    const matchPayStatus = payStatus.value === "all" || record.payStatus === payStatus.value;
    const matchKeyword =
      !keyword.value ||
      `${record.plate}${record.recordNo}${record.status}${record.payStatus}`.toLowerCase().includes(keyword.value.toLowerCase());

    const recordDate = record.enterAt.slice(0, 10);
    const matchDateFrom = !dateFrom.value || recordDate >= dateFrom.value;
    const matchDateTo = !dateTo.value || recordDate <= dateTo.value;

    return matchStatus && matchPayStatus && matchKeyword && matchDateFrom && matchDateTo;
  });
});

const canManageRecords = computed(() => userStore.canManageBusiness);
const canExportRecords = computed(() => userStore.canManageBusiness);
const permissionHint = computed(() => {
  if (!canManageRecords.value) {
    return "当前账号为只读模式，可查看记录与详情，但不支持模拟入场、模拟出场和导出数据。";
  }
  if (!canExportRecords.value) {
    return "当前账号可查看记录，但没有导出停车记录的权限。";
  }
  return "";
});

function buildQuery() {
  // 统一生成当前筛选条件，避免列表、统计与导出各自拼接参数。
  return {
    keyword: keyword.value || undefined,
    status: activeStatus.value === "all" ? undefined : activeStatus.value,
    payStatus: payStatus.value === "all" ? undefined : payStatus.value,
    dateFrom: dateFrom.value || undefined,
    dateTo: dateTo.value || undefined,
  };
}

function syncRouteQuery() {
  // 只保留有效筛选条件，避免地址栏堆积默认值。
  const nextQuery = Object.fromEntries(
    Object.entries(buildQuery()).filter(([, value]) => typeof value === "string" && value.length > 0),
  );
  void router.replace({ path: route.path, query: nextQuery });
}

function fillSummaryFromMock(data: RecordItem[]) {
  // 当后端不可用时，使用当前数据即时计算一份汇总，保证顶部卡片不留空。
  const paidItems = data.filter((item) => item.payStatus === "已支付");
  summary.totalCount = data.length;
  summary.inLotCount = data.filter((item) => item.status === "在场" || item.status === "超时在场").length;
  summary.departedCount = data.filter((item) => item.status === "已离场").length;
  summary.unpaidCount = data.filter((item) => item.payStatus === "未支付").length;
  summary.overdueCount = data.filter((item) => item.status === "超时在场").length;
  summary.totalAmount = paidItems.reduce((total, item) => total + Number(item.amount), 0).toFixed(2);
}

function resetEntryErrors() {
  entryErrors.plate_number = "";
  entryErrors.entry_gate = "";
  entryFormError.value = "";
}

function resetExitErrors() {
  exitErrors.plate_number = "";
  exitErrors.exit_gate = "";
  exitFormError.value = "";
}

function resetEntryForm() {
  entryForm.plate_number = "";
  entryForm.entry_gate = "";
  entryForm.space_id = "";
  entryForm.remark = "";
  resetEntryErrors();
}

function resetExitForm() {
  exitForm.plate_number = "";
  exitForm.exit_gate = "";
  exitForm.remark = "";
  resetExitErrors();
}

function validateEntryForm() {
  resetEntryErrors();

  if (!entryForm.plate_number) {
    entryErrors.plate_number = "请输入车牌号";
  } else if (entryForm.plate_number.length < 5) {
    entryErrors.plate_number = "车牌号长度不正确";
  }

  if (!entryForm.entry_gate) {
    entryErrors.entry_gate = "请输入入口通道";
  }

  return !entryErrors.plate_number && !entryErrors.entry_gate;
}

function validateExitForm() {
  resetExitErrors();

  if (!exitForm.plate_number) {
    exitErrors.plate_number = "请输入车牌号";
  } else if (exitForm.plate_number.length < 5) {
    exitErrors.plate_number = "车牌号长度不正确";
  }

  if (!exitForm.exit_gate) {
    exitErrors.exit_gate = "请输入出口通道";
  }

  return !exitErrors.plate_number && !exitErrors.exit_gate;
}

function goDetail(id: number) {
  // 详情页按主键跳转，便于后端直接查询单条记录。
  void router.push(`/records/${id}`);
}

async function fetchRecords() {
  try {
    const response = await getRecordList(buildQuery());
    records.value = response.data;
  } catch (error) {
    // 联调失败时回退到本地数据，保证演示页面仍可继续使用。
    records.value = parkingRecordsMock;
  }
}

async function fetchSummary() {
  try {
    const response = await getRecordSummary(buildQuery());
    Object.assign(summary, response.data);
  } catch (error) {
    fillSummaryFromMock(filteredRecords.value);
  }
}

async function fetchFreeSpaces() {
  if (!canManageRecords.value) {
    return;
  }

  try {
    const response = await getParkingSpaces({ status: "free" });
    freeSpaceOptions.value = response.data.filter((item) => item.type === "free");
  } catch (error) {
    freeSpaceOptions.value = [];
  }
}

async function refreshPageData() {
  // 模拟入场、出场完成后需要同时刷新列表、统计和空闲车位选择项。
  await fetchRecords();
  await fetchSummary();
  await fetchFreeSpaces();
}

function openEntryDrawer() {
  if (!canManageRecords.value) {
    appStore.showMessage("当前账号没有模拟入场的权限。", "warning");
    return;
  }
  resetEntryForm();
  entryDrawerVisible.value = true;
}

function closeEntryDrawer() {
  entryDrawerVisible.value = false;
}

function openExitDrawer() {
  if (!canManageRecords.value) {
    appStore.showMessage("当前账号没有模拟出场的权限。", "warning");
    return;
  }
  resetExitForm();
  exitDrawerVisible.value = true;
}

function closeExitDrawer() {
  exitDrawerVisible.value = false;
}

async function handleEntrySubmit() {
  if (!validateEntryForm()) {
    entryFormError.value = "请先修正入场表单中的错误信息。";
    return;
  }

  try {
    await createEntryRecord({
      plate_number: entryForm.plate_number,
      entry_gate: entryForm.entry_gate,
      space_id: entryForm.space_id ? Number(entryForm.space_id) : undefined,
      remark: entryForm.remark,
    });
    appStore.showMessage("模拟入场成功，停车记录已创建。", "success");
    closeEntryDrawer();
    await refreshPageData();
  } catch (error: any) {
    entryFormError.value = error?.response?.data?.message || "模拟入场失败，请稍后重试。";
    appStore.showMessage(entryFormError.value, "error");
  }
}

async function handleExitSubmit() {
  if (!validateExitForm()) {
    exitFormError.value = "请先修正出场表单中的错误信息。";
    return;
  }

  try {
    await settleExitRecord({
      plate_number: exitForm.plate_number,
      exit_gate: exitForm.exit_gate,
      remark: exitForm.remark,
    });
    appStore.showMessage("模拟出场成功，费用和车位状态已完成结算。", "success");
    closeExitDrawer();
    await refreshPageData();
  } catch (error: any) {
    exitFormError.value = error?.response?.data?.message || "模拟出场失败，请稍后重试。";
    appStore.showMessage(exitFormError.value, "error");
  }
}

async function handleExport() {
  if (!canExportRecords.value) {
    appStore.showMessage("当前账号没有导出停车记录的权限。", "warning");
    return;
  }

  try {
    const blob = await exportRecordList(buildQuery());
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `parking-records-${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    appStore.showMessage("停车记录已开始下载。", "success");
  } catch (error) {
    appStore.showMessage("导出失败，请确认后端服务是否可用。", "error");
  }
}

watch([keyword, activeStatus, payStatus, dateFrom, dateTo], async () => {
  syncRouteQuery();
  await fetchRecords();
  await fetchSummary();
});

watch(entryDrawerVisible, (visible) => {
  if (!visible) {
    resetEntryForm();
  }
});

watch(exitDrawerVisible, (visible) => {
  if (!visible) {
    resetExitForm();
  }
});

onMounted(async () => {
  syncRouteQuery();
  await refreshPageData();
});
</script>
