<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import {
  Calendar,
  Home,
  Inbox,
  Search,
  Settings,
  Moon,
  Sun,
  Info,
  TrendingUp,
  DollarSign,
  BarChart3,
  LineChart,
  User,
  LogOut,
  ChevronUp,
} from 'lucide-vue-next'
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter,
} from '@/components/ui/sidebar'
import { Switch } from '@/components/ui/switch'
import { DropdownMenu } from '@/components/ui/dropdown-menu'
import { DropdownMenuContent } from '@/components/ui/dropdown-menu'
import { DropdownMenuItem } from '@/components/ui/dropdown-menu'
import { DropdownMenuTrigger } from '@/components/ui/dropdown-menu'

// Menu items
const items = [
  {
    title: 'Dashboard',
    url: '#',
    icon: LineChart,
  },
]

// Theme management
const isDarkMode = ref(true)

// Check for user's preferred theme or saved preference
onMounted(() => {
  // Check if user has a saved preference
  const savedTheme = localStorage.getItem('theme')

  if (savedTheme) {
    // Apply saved theme preference
    isDarkMode.value = savedTheme === 'dark'
  } else {
    // Check if user prefers dark mode
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    isDarkMode.value = prefersDark
  }

  // Apply theme immediately on mount
  applyTheme()
})

// Apply theme whenever isDarkMode changes
watch(isDarkMode, () => {
  applyTheme()
})

function applyTheme() {
  // Update document class
  document.documentElement.classList.toggle('dark', isDarkMode.value)

  // Save preference to localStorage
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
}

function toggleTheme() {
  isDarkMode.value = !isDarkMode.value
}

// User profile
const username = ref('John Doe')
const isProfileOpen = ref(false)

const toggleProfileMenu = () => {
  isProfileOpen.value = !isProfileOpen.value
}
</script>

<template>
  <Sidebar variant="floating" collapsible="icon">
    <SidebarContent>
      <SidebarGroup>
        <SidebarGroupLabel class="flex items-center">
          <span class="text-copper font-bold text-xl">Vestra</span>
        </SidebarGroupLabel>
        <div class="text-sm italic mb-4">Invest More</div>
        <SidebarGroupContent>
          <SidebarMenu>
            <SidebarMenuItem v-for="item in items" :key="item.title">
              <SidebarMenuButton asChild>
                <a
                  :href="item.url"
                  class="flex items-center gap-2 px-2 py-2 rounded-md hover:bg-copper/10 transition-colors"
                >
                  <component :is="item.icon" class="h-5 w-5 text-copper" />
                  <span>{{ item.title }}</span>
                </a>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>

    <SidebarFooter class="border-t border-copper/30 pt-4 mt-auto">
      <div class="flex flex-col space-y-4 px-3">
        <!-- Theme Toggle -->
        <div class="flex items-center justify-between">
          <span class="text-sm">Theme</span>
          <div class="flex items-center gap-2">
            <Sun v-if="!isDarkMode" class="h-4 w-4 text-copper" />
            <Moon v-else class="h-4 w-4 text-copper" />
            <Switch :checked="isDarkMode" @update:checked="toggleTheme" />
          </div>
        </div>

        <!-- User Profile -->
        <DropdownMenu>
          <DropdownMenuTrigger
            class="flex items-center justify-between p-2 rounded-md hover:bg-copper/10 cursor-pointer"
          >
            <div class="flex items-center gap-2">
              <div
                class="h-8 w-8 rounded-full bg-copper flex items-center justify-center text-pale_white"
              >
                {{ username.charAt(0) }}
              </div>
              <span class="font-medium">{{ username }}</span>
            </div>
            <ChevronUp class="h-4 w-4" :class="{ 'rotate-180': !isProfileOpen }" />
          </DropdownMenuTrigger>

          <DropdownMenuContent align="end" class="w-56">
            <DropdownMenuItem class="cursor-pointer">
              <User class="mr-2 h-4 w-4" />
              <span>Account</span>
            </DropdownMenuItem>
            <DropdownMenuItem class="cursor-pointer">
              <Settings class="mr-2 h-4 w-4" />
              <span>Settings</span>
            </DropdownMenuItem>
            <DropdownMenuItem class="cursor-pointer text-red-500">
              <LogOut class="mr-2 h-4 w-4" />
              <span>Sign out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </SidebarFooter>
  </Sidebar>
</template>
