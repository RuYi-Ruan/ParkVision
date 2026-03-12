<template>
  <section class="page-stack">
    <article class="panel section-heading-card">
      <div>
        <h2>车位列表</h2>
        <p>展示车位基础信息，并支持通过右侧抽屉快速完成新增、编辑和删除操作。</p>
      </div>
      <div class="manage-panel__actions">
        <div class="filter-pills">
          <button
            v-for="item in parkingStatusFilters"
            :key="item.value"
            type="button"
            class="filter-pill"
            :class="{ 'filter-pill--active': activeStatus === item.value }"
            @click="activeStatus = item.value"
          >
            {{ item.label }}
          </button>
        </div>
        <button type="button" class="table-action table-action--primary" @click="openCreateDrawer">新增车位</button>
      </div>
    </article>

    <article class="panel toolbar-panel">
      <input v-model.trim="keyword" class="toolbar-search" type="text" placeholder="搜索车位编号或区域" />
      <div class="toolbar-summary">共筛选出 {{ filteredSpaces.length }} 个车位</div>
    </article>

    <article class="panel table-panel">
      <div class="table-header table-header--manage">
        <span>车位编号</span>
        <span>所属区域</span>
        <span>状态</span>
        <span>最近更新</span>
        <span>操作</span>
      </div>
      <div v-for="space in filteredSpaces" :key="space.id" class="table-row table-row--manage">
        <strong>{{ space.code }}</strong>
        <span>{{ space.zone }}</span>
        <span class="status-dot" :class="`status-dot--${space.type}`">{{ space.status }}</span>
        <span>{{ space.updatedAt }}</span>
        <div class="table-actions">
          <button type="button" class="table-action" @click="startEdit(space)">编辑</button>
          <div class="table-action-wrap">
            <button type="button" class="table-action table-action--danger" @click="toggleDeleteConfirm(space.id)">
              删除
            </button>
            <div v-if="confirmingDeleteId === space.id" class="popconfirm">
              <p class="popconfirm__title">确认删除车位 {{ space.code }} 吗？</p>
              <div class="popconfirm__actions">
                <button type="button" class="table-action" @click="confirmingDeleteId = null">取消</button>
                <button type="button" class="table-action table-action--danger" @click="handleDelete(space)">确认</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="!filteredSpaces.length" class="table-empty">没有符合条件的车位数据。</div>
    </article>

    <RightDrawer
      v-model="drawerVisible"
      :title="editingId ? '编辑车位' : '新增车位'"
      description="抽屉式编辑可以让列表保持在视线范围内，适合管理类页面连续操作。"
    >
      <div class="manage-form">
        <label>
          <span>车位编号</span>
          <input
            v-model.trim="form.space_code"
            :class="{ 'manage-form__input--error': Boolean(errors.space_code) }"
            type="text"
            placeholder="请输入车位编号"
          />
          <small v-if="errors.space_code" class="manage-form__field-error">{{ errors.space_code }}</small>
        </label>
        <label>
          <span>所属区域</span>
          <input
            v-model.trim="form.area_code"
            :class="{ 'manage-form__input--error': Boolean(errors.area_code) }"
            type="text"
            placeholder="如：A 区地面"
          />
          <small v-if="errors.area_code" class="manage-form__field-error">{{ errors.area_code }}</small>
        </label>
        <label>
          <span>车位类型</span>
          <input
            v-model.trim="form.space_type"
            :class="{ 'manage-form__input--error': Boolean(errors.space_type) }"
            type="text"
            placeholder="如：普通车位"
          />
          <small v-if="errors.space_type" class="manage-form__field-error">{{ errors.space_type }}</small>
        </label>
        <label>
          <span>状态</span>
          <select v-model="form.status">
            <option value="空闲">空闲</option>
            <option value="占用">占用</option>
            <option value="维护">维护</option>
          </select>
        </label>
        <label>
          <span>楼层</span>
          <input v-model.trim="form.floor_no" type="text" placeholder="如：1F / B1" />
        </label>
        <label class="manage-form__wide">
          <span>备注</span>
          <input v-model.trim="form.remark" type="text" placeholder="可填写充电桩、维修中等说明" />
        </label>
      </div>

      <p v-if="formError" class="manage-panel__error">{{ formError }}</p>

      <template #footer>
        <button type="button" class="table-action" @click="closeDrawer">取消</button>
        <button type="button" class="table-action table-action--primary" @click="handleSubmit">
          {{ editingId ? "保存修改" : "新增车位" }}
        </button>
      </template>
    </RightDrawer>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";

import RightDrawer from "@/components/RightDrawer.vue";
import {
  createParkingSpace,
  deleteParkingSpace,
  getParkingSpaces,
  updateParkingSpace,
  type ParkingSpaceFormData,
} from "@/api/parking";
import { parkingSpaces as parkingSpacesMock, parkingStatusFilters } from "@/mock/parking";
import { useAppStore } from "@/store/app";
import type { ParkingSpaceItem } from "@/types/domain";

type SpaceStatus = "all" | "free" | "busy" | "warning";
type SpaceFormErrors = Record<"space_code" | "area_code" | "space_type", string>;

const appStore = useAppStore();
const keyword = ref("");
const activeStatus = ref<SpaceStatus>("all");
const spaces = ref<ParkingSpaceItem[]>(parkingSpacesMock);
const editingId = ref<number | null>(null);
const formError = ref("");
const drawerVisible = ref(false);
const confirmingDeleteId = ref<number | null>(null);

// 表单字段直接与后端写入接口保持一致，避免额外转换。
const form = reactive<ParkingSpaceFormData>({
  space_code: "",
  area_code: "",
  space_type: "普通车位",
  status: "空闲",
  floor_no: "",
  remark: "",
});

const errors = reactive<SpaceFormErrors>({
  space_code: "",
  area_code: "",
  space_type: "",
});

const filteredSpaces = computed(() => {
  // 即使后端已支持筛选，前端仍保留同构过滤逻辑，以兼容 mock 回退场景。
  return spaces.value.filter((space) => {
    const matchStatus = activeStatus.value === "all" || space.type === activeStatus.value;
    const matchKeyword =
      !keyword.value || `${space.code}${space.zone}${space.status}`.toLowerCase().includes(keyword.value.toLowerCase());

    return matchStatus && matchKeyword;
  });
});

function clearErrors() {
  errors.space_code = "";
  errors.area_code = "";
  errors.space_type = "";
  formError.value = "";
}

function validateForm() {
  clearErrors();

  if (!form.space_code) {
    errors.space_code = "请输入车位编号";
  }

  if (!form.area_code) {
    errors.area_code = "请输入所属区域";
  }

  if (!form.space_type) {
    errors.space_type = "请输入车位类型";
  }

  return !errors.space_code && !errors.area_code && !errors.space_type;
}

function resetForm() {
  editingId.value = null;
  form.space_code = "";
  form.area_code = "";
  form.space_type = "普通车位";
  form.status = "空闲";
  form.floor_no = "";
  form.remark = "";
  clearErrors();
}

function openCreateDrawer() {
  // 新增时先清空旧编辑状态，再打开抽屉。
  resetForm();
  drawerVisible.value = true;
}

function closeDrawer() {
  drawerVisible.value = false;
}

function startEdit(space: ParkingSpaceItem) {
  // 编辑时把列表项映射回表单字段，保证操作路径足够直接。
  editingId.value = space.id;
  clearErrors();
  form.space_code = space.code;
  form.area_code = space.zone;
  form.space_type = space.spaceType || "普通车位";
  form.status = space.status;
  form.floor_no = space.floorNo || "";
  form.remark = space.remark || "";
  drawerVisible.value = true;
}

function toggleDeleteConfirm(id: number) {
  // 同一时间只允许展开一个删除确认框，避免页面上出现多个确认气泡。
  confirmingDeleteId.value = confirmingDeleteId.value === id ? null : id;
}

async function fetchSpaces() {
  try {
    // 将工具栏的筛选状态直接映射为接口参数，保证页面表现与请求条件一致。
    const response = await getParkingSpaces({
      keyword: keyword.value || undefined,
      status: activeStatus.value === "all" ? undefined : activeStatus.value,
    });
    spaces.value = response.data;
  } catch (error) {
    // 联调失败时回退到本地数据，避免演示页面直接空白。
    spaces.value = parkingSpacesMock;
  }
}

async function handleSubmit() {
  if (!validateForm()) {
    formError.value = "请先修正表单中的错误信息。";
    return;
  }

  try {
    if (editingId.value) {
      await updateParkingSpace(editingId.value, { ...form });
      appStore.showMessage("车位信息已更新", "success");
    } else {
      await createParkingSpace({ ...form });
      appStore.showMessage("车位新增成功", "success");
    }

    closeDrawer();
    await fetchSpaces();
  } catch (error: any) {
    formError.value = error?.response?.data?.message || "车位保存失败，请稍后重试。";
    appStore.showMessage(formError.value, "error");
  }
}

async function handleDelete(space: ParkingSpaceItem) {
  try {
    await deleteParkingSpace(space.id);
    confirmingDeleteId.value = null;
    if (editingId.value === space.id) {
      closeDrawer();
    }
    appStore.showMessage(`车位 ${space.code} 已删除`, "success");
    await fetchSpaces();
  } catch (error: any) {
    formError.value = error?.response?.data?.message || "车位删除失败，请稍后重试。";
    appStore.showMessage(formError.value, "error");
  }
}

watch([keyword, activeStatus], () => {
  void fetchSpaces();
});

watch(drawerVisible, (visible) => {
  // 抽屉关闭时同步清空表单，避免下次打开仍停留在旧状态。
  if (!visible) {
    resetForm();
  }
});

onMounted(() => {
  void fetchSpaces();
});
</script>
