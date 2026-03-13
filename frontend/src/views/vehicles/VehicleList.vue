<template>
  <section class="page-stack">
    <article class="panel section-heading-card">
      <div>
        <h2>车辆管理</h2>
        <p>展示车辆基础信息，并支持通过右侧抽屉快速完成新增、编辑和删除操作。</p>
      </div>
      <div class="manage-panel__actions">
        <div class="filter-pills">
          <button
            v-for="item in vehicleStatusFilters"
            :key="item.value"
            type="button"
            class="filter-pill"
            :class="{ 'filter-pill--active': activeStatus === item.value }"
            @click="activeStatus = item.value"
          >
            {{ item.label }}
          </button>
        </div>
        <button
          v-if="canManageVehicles"
          type="button"
          class="table-action table-action--primary"
          @click="openCreateDrawer"
        >
          新增车辆
        </button>
      </div>
    </article>

    <article class="panel toolbar-panel">
      <input v-model.trim="keyword" class="toolbar-search" type="text" placeholder="搜索车牌号、车主或车辆类型" />
      <div class="toolbar-summary">共筛选出 {{ filteredVehicles.length }} 辆车</div>
    </article>

    <article v-if="!canManageVehicles" class="panel">
      <p class="manage-panel__error">当前账号为只读模式，可查看车辆详情和停车记录，但不能新增、编辑或删除车辆。</p>
    </article>

    <article class="panel table-panel">
      <div class="table-header table-header--vehicles table-header--manage">
        <span>车牌号</span>
        <span>车主</span>
        <span>车辆类型</span>
        <span>备注</span>
        <span>状态</span>
        <span>操作</span>
      </div>
      <div v-for="vehicle in filteredVehicles" :key="vehicle.id" class="table-row table-row--vehicles table-row--manage">
        <button type="button" class="table-link-button" @click="viewVehicleDetail(vehicle.id)">
          {{ vehicle.plate }}
        </button>
        <span>{{ vehicle.owner }}</span>
        <span>{{ vehicle.category }}</span>
        <span>{{ vehicle.space }}</span>
        <span class="status-dot status-dot--compact" :class="`status-dot--${vehicle.type}`">{{ vehicle.status }}</span>
        <div class="table-actions table-actions--end">
          <div v-if="canManageVehicles" class="table-action-group">
            <button type="button" class="table-action table-action--link" @click="viewVehicleRecords(vehicle.plate)">查看记录</button>
            <button
              type="button"
              class="table-action table-action--link table-action--link-edit"
              @click="startEdit(vehicle)"
            >
              编辑
            </button>
            <div class="table-action-wrap">
              <button
                type="button"
                class="table-action table-action--link table-action--link-danger"
                @click="toggleDeleteConfirm(vehicle.id)"
              >
                删除
              </button>
              <div v-if="confirmingDeleteId === vehicle.id" class="popconfirm">
                <p class="popconfirm__title">确认删除车辆 {{ vehicle.plate }} 吗？</p>
                <div class="popconfirm__actions">
                  <button type="button" class="table-action" @click="confirmingDeleteId = null">取消</button>
                  <button type="button" class="table-action table-action--danger" @click="handleDelete(vehicle)">确认</button>
                </div>
              </div>
            </div>
          </div>
          <button v-else type="button" class="table-action table-action--link" @click="viewVehicleRecords(vehicle.plate)">查看记录</button>
        </div>
      </div>
      <div v-if="!filteredVehicles.length" class="table-empty">没有符合条件的车辆数据。</div>
    </article>

    <RightDrawer
      v-if="canManageVehicles"
      v-model="drawerVisible"
      :title="editingId ? '编辑车辆' : '新增车辆'"
      description="在抽屉中维护车辆信息，列表会保持在当前视线范围内。"
    >
      <div class="manage-form">
        <label>
          <span>车牌号</span>
          <input
            v-model.trim="form.plate_number"
            :class="{ 'manage-form__input--error': Boolean(errors.plate_number) }"
            type="text"
            placeholder="请输入车牌号"
          />
          <small v-if="errors.plate_number" class="manage-form__field-error">{{ errors.plate_number }}</small>
        </label>
        <label>
          <span>车主</span>
          <input
            v-model.trim="form.owner_name"
            :class="{ 'manage-form__input--error': Boolean(errors.owner_name) }"
            type="text"
            placeholder="请输入车主姓名"
          />
          <small v-if="errors.owner_name" class="manage-form__field-error">{{ errors.owner_name }}</small>
        </label>
        <label>
          <span>联系电话</span>
          <input
            v-model.trim="form.owner_phone"
            :class="{ 'manage-form__input--error': Boolean(errors.owner_phone) }"
            type="text"
            placeholder="请输入联系电话"
          />
          <small v-if="errors.owner_phone" class="manage-form__field-error">{{ errors.owner_phone }}</small>
        </label>
        <label>
          <span>车辆类型</span>
          <input
            v-model.trim="form.vehicle_type"
            :class="{ 'manage-form__input--error': Boolean(errors.vehicle_type) }"
            type="text"
            placeholder="如：新能源轿车"
          />
          <small v-if="errors.vehicle_type" class="manage-form__field-error">{{ errors.vehicle_type }}</small>
        </label>
        <label>
          <span>车身颜色</span>
          <input v-model.trim="form.color" type="text" placeholder="请输入车身颜色" />
        </label>
        <label>
          <span>状态</span>
          <select v-model.number="form.status">
            <option :value="1">已备案</option>
            <option :value="0">停用</option>
          </select>
        </label>
        <label class="manage-form__wide">
          <span>备注</span>
          <input v-model.trim="form.remark" type="text" placeholder="可填写固定车、月租车等说明" />
        </label>
      </div>

      <p v-if="formError" class="manage-panel__error">{{ formError }}</p>

      <template #footer>
        <button type="button" class="table-action" @click="closeDrawer">取消</button>
        <button type="button" class="table-action table-action--primary" @click="handleSubmit">
          {{ editingId ? "保存修改" : "新增车辆" }}
        </button>
      </template>
    </RightDrawer>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import RightDrawer from "@/components/RightDrawer.vue";
import { createVehicle, deleteVehicle, getVehicleList, updateVehicle, type VehicleFormData } from "@/api/vehicle";
import { vehicleStatusFilters, vehicles as vehiclesMock } from "@/mock/vehicles";
import { useAppStore } from "@/store/app";
import { useUserStore } from "@/store/user";
import type { VehicleItem } from "@/types/domain";

type VehicleStatus = "all" | "free" | "warning";
type VehicleFormErrors = Record<"plate_number" | "owner_name" | "owner_phone" | "vehicle_type", string>;

const appStore = useAppStore();
const userStore = useUserStore();
const route = useRoute();
const router = useRouter();
const keyword = ref("");
const activeStatus = ref<VehicleStatus>("all");
const vehicles = ref<VehicleItem[]>(vehiclesMock);
const editingId = ref<number | null>(null);
const formError = ref("");
const drawerVisible = ref(false);
const confirmingDeleteId = ref<number | null>(null);

// 表单字段直接与后端写入接口保持一致，避免额外转换。
const form = reactive<VehicleFormData>({
  plate_number: "",
  owner_name: "",
  owner_phone: "",
  vehicle_type: "",
  color: "",
  status: 1,
  remark: "",
});

const errors = reactive<VehicleFormErrors>({
  plate_number: "",
  owner_name: "",
  owner_phone: "",
  vehicle_type: "",
});

const filteredVehicles = computed(() => {
  // 即使后端已支持筛选，前端仍保留同构过滤逻辑，以兼容 mock 回退场景。
  return vehicles.value.filter((vehicle) => {
    const matchStatus = activeStatus.value === "all" || vehicle.type === activeStatus.value;
    const matchKeyword =
      !keyword.value ||
      `${vehicle.plate}${vehicle.owner}${vehicle.category}${vehicle.space}`.toLowerCase().includes(keyword.value.toLowerCase());

    return matchStatus && matchKeyword;
  });
});

const canManageVehicles = computed(() => userStore.canManageBusiness);

function normalizeVehicleStatus(value: unknown): VehicleStatus {
  return value === "free" || value === "warning" ? value : "all";
}

function applyQueryFilters() {
  // 车辆页允许从其他页面带车牌或状态条件进入，便于形成页面联动。
  keyword.value = typeof route.query.keyword === "string" ? route.query.keyword : "";
  activeStatus.value = normalizeVehicleStatus(route.query.status);
}

async function syncQueryAndFetch() {
  await router.replace({
    query: {
      keyword: keyword.value || undefined,
      status: activeStatus.value === "all" ? undefined : activeStatus.value,
    },
  });
  await fetchVehicles();
}

function viewVehicleDetail(id: number) {
  // 车辆详情页承接记录详情、车辆列表等多个入口。
  void router.push(`/vehicles/${id}`);
}

function viewVehicleRecords(plate: string) {
  // 从车辆页直接跳到停车记录页，并按车牌预填关键词，缩短追踪链路。
  void router.push({
    path: "/records",
    query: {
      keyword: plate,
    },
  });
}

function clearErrors() {
  errors.plate_number = "";
  errors.owner_name = "";
  errors.owner_phone = "";
  errors.vehicle_type = "";
  formError.value = "";
}

function validateForm() {
  clearErrors();

  if (!form.plate_number) {
    errors.plate_number = "请输入车牌号";
  } else if (form.plate_number.length < 5) {
    errors.plate_number = "车牌号长度不正确";
  }

  if (!form.owner_name) {
    errors.owner_name = "请输入车主姓名";
  }

  if (form.owner_phone && !/^1\d{10}$/.test(form.owner_phone)) {
    errors.owner_phone = "请输入正确的手机号";
  }

  if (!form.vehicle_type) {
    errors.vehicle_type = "请输入车辆类型";
  }

  return !errors.plate_number && !errors.owner_name && !errors.owner_phone && !errors.vehicle_type;
}

function resetForm() {
  editingId.value = null;
  form.plate_number = "";
  form.owner_name = "";
  form.owner_phone = "";
  form.vehicle_type = "";
  form.color = "";
  form.status = 1;
  form.remark = "";
  clearErrors();
}

function openCreateDrawer() {
  if (!canManageVehicles.value) {
    appStore.showMessage("当前账号没有新增车辆的权限。", "warning");
    return;
  }
  // 新增时先清空旧编辑状态，再打开抽屉。
  resetForm();
  drawerVisible.value = true;
}

function closeDrawer() {
  drawerVisible.value = false;
}

function startEdit(vehicle: VehicleItem) {
  if (!canManageVehicles.value) {
    appStore.showMessage("当前账号没有编辑车辆的权限。", "warning");
    return;
  }
  // 编辑时把列表项映射回表单字段，保证操作路径足够直接。
  editingId.value = vehicle.id;
  clearErrors();
  form.plate_number = vehicle.plate;
  form.owner_name = vehicle.owner;
  form.owner_phone = vehicle.ownerPhone || "";
  form.vehicle_type = vehicle.category;
  form.color = vehicle.color || "";
  form.status = vehicle.statusValue ?? (vehicle.type === "free" ? 1 : 0);
  form.remark = vehicle.space === "--" ? "" : vehicle.space;
  drawerVisible.value = true;
}

function toggleDeleteConfirm(id: number) {
  if (!canManageVehicles.value) {
    appStore.showMessage("当前账号没有删除车辆的权限。", "warning");
    return;
  }
  // 同一时间只允许展开一个删除确认框，避免页面上出现多个确认气泡。
  confirmingDeleteId.value = confirmingDeleteId.value === id ? null : id;
}

async function fetchVehicles() {
  try {
    // 将工具栏状态映射为查询参数，保证页面显示和接口条件保持一致。
    const response = await getVehicleList({
      keyword: keyword.value || undefined,
      status: activeStatus.value === "all" ? undefined : activeStatus.value,
    });
    vehicles.value = response.data;
  } catch (error) {
    // 联调失败时回退到本地 mock，避免页面直接空白。
    vehicles.value = vehiclesMock;
  }
}

async function handleSubmit() {
  if (!validateForm()) {
    formError.value = "请先修正表单中的错误信息。";
    return;
  }

  try {
    if (editingId.value) {
      await updateVehicle(editingId.value, { ...form });
      appStore.showMessage("车辆信息已更新", "success");
    } else {
      await createVehicle({ ...form });
      appStore.showMessage("车辆新增成功", "success");
    }

    closeDrawer();
    await fetchVehicles();
  } catch (error: any) {
    formError.value = error?.response?.data?.message || "车辆保存失败，请稍后重试。";
    appStore.showMessage(formError.value, "error");
  }
}

async function handleDelete(vehicle: VehicleItem) {
  try {
    await deleteVehicle(vehicle.id);
    confirmingDeleteId.value = null;
    if (editingId.value === vehicle.id) {
      closeDrawer();
    }
    appStore.showMessage(`车辆 ${vehicle.plate} 已删除`, "success");
    await fetchVehicles();
  } catch (error: any) {
    formError.value = error?.response?.data?.message || "车辆删除失败，请稍后重试。";
    appStore.showMessage(formError.value, "error");
  }
}

watch([keyword, activeStatus], () => {
  void syncQueryAndFetch();
});

watch(drawerVisible, (visible) => {
  // 抽屉关闭时同步清空表单，避免下次打开仍停留在旧状态。
  if (!visible) {
    resetForm();
  }
});

watch(
  () => route.query,
  () => {
    applyQueryFilters();
  },
);

onMounted(() => {
  applyQueryFilters();
  void fetchVehicles();
});
</script>
