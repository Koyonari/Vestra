<script setup lang="ts">
import { ref } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
import { SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
const title = ref('Market Sentiment')
const subtitle = ref('The market is going to be up')
const status = ref('pending')
const balls = ref(0)
</script>

<template>
  <div class="p-4">
    <h1 class="text-2xl font-bold">{{ title }}</h1>
    <h2 class="text-xl">{{ subtitle }}</h2>
    <p>Number of balls: {{ balls }}</p>
    <Button v-if="status === 'active'" className="border-4 border-blue-500">Click me</Button>
    <Button v-else-if="status === 'pending'">Button is pending</Button>
    <Button v-else>Don't click me</Button>
  </div>

  <SidebarProvider>
    <AppSidebar />
    <main>
      <SidebarTrigger />
      <RouterView />
    </main>
  </SidebarProvider>
</template>
