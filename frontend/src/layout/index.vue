<template>
  <div class="app-shell">
    <Sidebar />
    <div class="app-main">
      <Header />
      <main class="app-content">
        <RouterView v-slot="{ Component }">
          <Transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </Transition>
        </RouterView>
      </main>
      <Footer />
    </div>
  </div>
</template>

<script setup lang="ts">
import Footer from "./Footer.vue";
import Header from "./Header.vue";
import Sidebar from "./Sidebar.vue";
</script>
