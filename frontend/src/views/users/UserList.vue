<template>
  <section class="page-stack">
    <article class="panel section-heading-card">
      <div>
        <h2>用户管理</h2>
        <p>维护后台账号、角色和启停状态，补齐系统管理能力，为后续权限细化打基础。</p>
      </div>
      <div class="manage-panel__actions">
        <div class="filter-pills">
          <button
            v-for="item in userStatusFilters"
            :key="item.value"
            type="button"
            class="filter-pill"
            :class="{ 'filter-pill--active': activeStatus === item.value }"
            @click="activeStatus = item.value"
          >
            {{ item.label }}
          </button>
        </div>
        <button type="button" class="table-action table-action--primary" @click="openCreateDrawer">新增用户</button>
      </div>
    </article>

    <article class="panel toolbar-panel toolbar-panel--records">
      <div class="records-filter-grid">
        <div class="toolbar-field">
          <span class="toolbar-field__label">关键词</span>
          <input v-model.trim="keyword" class="toolbar-search" type="text" placeholder="搜索账号、姓名或手机号" />
        </div>
        <div class="toolbar-field">
          <span class="toolbar-field__label">角色</span>
          <select v-model="activeRole" class="toolbar-select">
            <option v-for="item in userRoleFilters" :key="item.value" :value="item.value">
              {{ item.label }}
            </option>
          </select>
        </div>
      </div>
      <div class="toolbar-summary toolbar-summary--records">共筛选出 {{ filteredUsers.length }} 个账号</div>
    </article>

    <article class="panel table-panel">
      <div class="table-scroll">
        <div class="table-header table-header--users">
          <span>登录账号</span>
          <span>姓名</span>
          <span>角色</span>
          <span>手机号</span>
          <span>最后登录</span>
          <span>状态</span>
          <span>操作</span>
        </div>
        <div v-for="user in filteredUsers" :key="user.id" class="table-row table-row--users">
          <strong>{{ user.username }}</strong>
          <span>{{ user.realName }}</span>
          <span>{{ user.roleName }}</span>
          <span>{{ user.phone }}</span>
          <span>{{ user.lastLogin }}</span>
          <span class="status-dot status-dot--compact" :class="`status-dot--${user.type}`">{{ user.status }}</span>
          <div class="table-actions table-actions--end">
            <div class="table-action-group">
              <button type="button" class="table-action table-action--link table-action--link-edit" @click="startEdit(user)">编辑</button>
              <div class="table-action-wrap">
                <button
                  type="button"
                  class="table-action table-action--link table-action--link-danger"
                  @click="toggleDeleteConfirm(user.id)"
                >
                  删除
                </button>
                <div v-if="confirmingDeleteId === user.id" class="popconfirm">
                  <p class="popconfirm__title">确认删除账号 {{ user.username }} 吗？</p>
                  <div class="popconfirm__actions">
                    <button type="button" class="table-action" @click="confirmingDeleteId = null">取消</button>
                    <button type="button" class="table-action table-action--danger" @click="handleDelete(user)">确认</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="!filteredUsers.length" class="table-empty">没有符合条件的用户数据。</div>
      </div>
    </article>

    <RightDrawer
      v-model="drawerVisible"
      :title="editingId ? '编辑用户' : '新增用户'"
      description="在抽屉中维护账号信息和角色配置，保持用户列表始终可见。"
    >
      <div class="manage-form">
        <label>
          <span>登录账号</span>
          <input
            v-model.trim="form.username"
            :class="{ 'manage-form__input--error': Boolean(errors.username) }"
            type="text"
            placeholder="请输入登录账号"
          />
          <small v-if="errors.username" class="manage-form__field-error">{{ errors.username }}</small>
        </label>
        <label>
          <span>登录密码</span>
          <input
            v-model.trim="form.password"
            :class="{ 'manage-form__input--error': Boolean(errors.password) }"
            type="text"
            placeholder="请输入登录密码"
          />
          <small v-if="errors.password" class="manage-form__field-error">{{ errors.password }}</small>
        </label>
        <label>
          <span>姓名</span>
          <input
            v-model.trim="form.real_name"
            :class="{ 'manage-form__input--error': Boolean(errors.real_name) }"
            type="text"
            placeholder="请输入真实姓名"
          />
          <small v-if="errors.real_name" class="manage-form__field-error">{{ errors.real_name }}</small>
        </label>
        <label>
          <span>手机号</span>
          <input
            v-model.trim="form.phone"
            :class="{ 'manage-form__input--error': Boolean(errors.phone) }"
            type="text"
            placeholder="请输入手机号"
          />
          <small v-if="errors.phone" class="manage-form__field-error">{{ errors.phone }}</small>
        </label>
        <label>
          <span>角色</span>
          <select v-model="form.role">
            <option value="admin">系统管理员</option>
            <option value="operator">值班管理员</option>
            <option value="viewer">只读用户</option>
          </select>
        </label>
        <label>
          <span>状态</span>
          <select v-model.number="form.status">
            <option :value="1">启用</option>
            <option :value="0">停用</option>
          </select>
        </label>
      </div>

      <p v-if="formError" class="manage-panel__error">{{ formError }}</p>

      <template #footer>
        <button type="button" class="table-action" @click="closeDrawer">取消</button>
        <button type="button" class="table-action table-action--primary" @click="handleSubmit">
          {{ editingId ? "保存修改" : "新增用户" }}
        </button>
      </template>
    </RightDrawer>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";

import RightDrawer from "@/components/RightDrawer.vue";
import { createUser, deleteUser, getUserList, updateUser, type UserFormData } from "@/api/user";
import { userRoleFilters, usersMock, userStatusFilters } from "@/mock/users";
import { useAppStore } from "@/store/app";
import type { UserItem } from "@/types/domain";

type UserStatus = "all" | "free" | "warning";
type UserRole = "all" | "admin" | "operator" | "viewer";
type UserFormErrors = Record<"username" | "password" | "real_name" | "phone", string>;

const appStore = useAppStore();
const keyword = ref("");
const activeStatus = ref<UserStatus>("all");
const activeRole = ref<UserRole>("all");
const users = ref<UserItem[]>(usersMock);
const editingId = ref<number | null>(null);
const formError = ref("");
const drawerVisible = ref(false);
const confirmingDeleteId = ref<number | null>(null);

// 用户表单字段直接与后端写入接口保持一致，减少转换复杂度。
const form = reactive<UserFormData>({
  username: "",
  password: "",
  real_name: "",
  phone: "",
  role: "operator",
  status: 1,
});

const errors = reactive<UserFormErrors>({
  username: "",
  password: "",
  real_name: "",
  phone: "",
});

const filteredUsers = computed(() => {
  // 即使后端已经支持筛选，前端仍保留同构过滤，兼容 mock 回退场景。
  return users.value.filter((user) => {
    const matchStatus = activeStatus.value === "all" || user.type === activeStatus.value;
    const matchRole = activeRole.value === "all" || user.role === activeRole.value;
    const matchKeyword =
      !keyword.value ||
      `${user.username}${user.realName}${user.phone}${user.roleName}`.toLowerCase().includes(keyword.value.toLowerCase());

    return matchStatus && matchRole && matchKeyword;
  });
});

function clearErrors() {
  errors.username = "";
  errors.password = "";
  errors.real_name = "";
  errors.phone = "";
  formError.value = "";
}

function validateForm() {
  clearErrors();

  if (!form.username) {
    errors.username = "请输入登录账号";
  }

  if (!form.password) {
    errors.password = "请输入登录密码";
  } else if (form.password.length < 6) {
    errors.password = "密码长度至少为 6 位";
  }

  if (!form.real_name) {
    errors.real_name = "请输入真实姓名";
  }

  if (form.phone && !/^1\d{10}$/.test(form.phone)) {
    errors.phone = "请输入正确的手机号";
  }

  return !errors.username && !errors.password && !errors.real_name && !errors.phone;
}

function resetForm() {
  editingId.value = null;
  form.username = "";
  form.password = "";
  form.real_name = "";
  form.phone = "";
  form.role = "operator";
  form.status = 1;
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

function startEdit(user: UserItem) {
  // 编辑时把列表项映射回表单字段，保证操作路径直接。
  editingId.value = user.id;
  clearErrors();
  form.username = user.username;
  form.password = "123456";
  form.real_name = user.realName;
  form.phone = user.phone === "--" ? "" : user.phone;
  form.role = user.role as UserFormData["role"];
  form.status = user.statusValue;
  drawerVisible.value = true;
}

function toggleDeleteConfirm(id: number) {
  // 同一时间只展开一个删除确认框，避免页面出现多个确认气泡。
  confirmingDeleteId.value = confirmingDeleteId.value === id ? null : id;
}

async function fetchUsers() {
  try {
    const response = await getUserList({
      keyword: keyword.value || undefined,
      status: activeStatus.value === "all" ? undefined : activeStatus.value,
      role: activeRole.value === "all" ? undefined : activeRole.value,
    });
    users.value = response.data;
  } catch (error) {
    // 联调失败时回退到本地 mock，保证页面仍可演示。
    users.value = usersMock;
  }
}

async function handleSubmit() {
  if (!validateForm()) {
    formError.value = "请先修正表单中的错误信息。";
    return;
  }

  try {
    if (editingId.value) {
      await updateUser(editingId.value, { ...form });
      appStore.showMessage("用户信息已更新", "success");
    } else {
      await createUser({ ...form });
      appStore.showMessage("用户新增成功", "success");
    }

    closeDrawer();
    await fetchUsers();
  } catch (error: any) {
    formError.value = error?.response?.data?.message || "用户保存失败，请稍后重试。";
    appStore.showMessage(formError.value, "error");
  }
}

async function handleDelete(user: UserItem) {
  try {
    await deleteUser(user.id);
    confirmingDeleteId.value = null;
    if (editingId.value === user.id) {
      closeDrawer();
    }
    appStore.showMessage(`用户 ${user.username} 已删除`, "success");
    await fetchUsers();
  } catch (error: any) {
    formError.value = error?.response?.data?.message || "用户删除失败，请稍后重试。";
    appStore.showMessage(formError.value, "error");
  }
}

watch([keyword, activeStatus, activeRole], () => {
  void fetchUsers();
});

watch(drawerVisible, (visible) => {
  // 抽屉关闭时同步清空表单，避免下次打开仍停留在旧状态。
  if (!visible) {
    resetForm();
  }
});

onMounted(() => {
  void fetchUsers();
});
</script>
