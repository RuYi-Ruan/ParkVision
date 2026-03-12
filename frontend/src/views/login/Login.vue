<template>
  <div class="auth-page">
    <section class="auth-hero">
      <p class="eyebrow">Smart Parking Command Center</p>
      <div class="auth-hero__headline">
        <span class="auth-hero__badge">ParkVision</span>
        <h1>把停车场运营信息收拢到一个清晰的管理界面里。</h1>
      </div>
      <p class="auth-hero__desc">
        面向毕业设计的停车场管理平台，聚合车位监控、车辆管理、记录查询与识别测试模块。
      </p>
      <div class="auth-hero__cards">
        <div class="auth-hero__card">
          <strong>120</strong>
          <span>总车位</span>
        </div>
        <div class="auth-hero__card">
          <strong>97.2%</strong>
          <span>车牌识别率</span>
        </div>
        <div class="auth-hero__card">
          <strong>24h</strong>
          <span>在线监控</span>
        </div>
      </div>
    </section>

    <section class="auth-card auth-card--form">
      <p class="eyebrow">管理员入口</p>
      <h2>登录 ParkVision</h2>
      <p class="auth-card__desc">演示账号为 `admin`，密码为 `123456`。</p>

      <form class="auth-form" @submit.prevent="handleLogin">
        <label class="auth-form__field">
          <span>账号</span>
          <input
            v-model.trim="form.username"
            :class="{ 'auth-form__input--error': Boolean(errors.username) }"
            type="text"
            placeholder="请输入管理员账号"
          />
          <small v-if="errors.username" class="auth-form__error">{{ errors.username }}</small>
        </label>

        <label class="auth-form__field">
          <span>密码</span>
          <input
            v-model="form.password"
            :class="{ 'auth-form__input--error': Boolean(errors.password) }"
            type="password"
            placeholder="请输入登录密码"
          />
          <small v-if="errors.password" class="auth-form__error">{{ errors.password }}</small>
        </label>

        <p v-if="errors.form" class="auth-form__error auth-form__error--block">{{ errors.form }}</p>
        <button class="auth-form__submit" type="submit">{{ submitting ? "登录中..." : "进入系统" }}</button>
      </form>
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { login } from "@/api/auth";
import { useUserStore } from "@/store/user";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

// 默认填入演示账号，便于阶段汇报和联调演示时快速进入系统。
const form = reactive({
  username: "admin",
  password: "123456",
});

const errors = reactive({
  username: "",
  password: "",
  form: "",
});

const submitting = ref(false);

function validate() {
  // 每次提交前都先清空旧错误，避免错误提示残留。
  errors.username = "";
  errors.password = "";
  errors.form = "";

  if (!form.username) {
    errors.username = "请输入账号";
  } else if (form.username.length < 3) {
    errors.username = "账号至少 3 个字符";
  }

  if (!form.password) {
    errors.password = "请输入密码";
  } else if (form.password.length < 6) {
    errors.password = "密码至少 6 位";
  }

  return !errors.username && !errors.password;
}

async function handleLogin() {
  // 先做前端校验，减少无效请求，也能给用户更即时的反馈。
  if (!validate()) {
    return;
  }

  submitting.value = true;

  try {
    const response = await login({
      username: form.username,
      password: form.password,
    });

    // 先写入 token，再跳转页面，这样路由守卫不会拦截目标页。
    userStore.setToken(response.data.token);
    userStore.setProfile(response.data.username, response.data.role_name);

    const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "/dashboard";
    void router.push(redirect);
  } catch (error) {
    errors.form = "账号或密码不正确，请使用演示账号登录。";
  } finally {
    submitting.value = false;
  }
}
</script>
