<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Settings, Moon, Sun, LineChart, User, LogOut, ChevronUp } from 'lucide-vue-next'
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
import { useSidebar } from '@/components/ui/sidebar/utils'

const { state, isMobile } = useSidebar()

// Menu items
const items = [
  {
    title: 'Stock Dashboard',
    url: '#',
    icon: LineChart,
  },
]

// User profile
const username = ref('John Doe')
const isProfileOpen = ref(false)
const toggleProfileMenu = () => {
  isProfileOpen.value = !isProfileOpen.value
}

// Theme management
const isDarkMode = ref(false)

// Function to toggle between dark and light mode
const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  applyTheme()
}

// Function to apply the theme
const applyTheme = () => {
  console.log('Applying theme:', isDarkMode.value ? 'dark' : 'light') // Debug log

  if (isDarkMode.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

// Check for saved theme preference or respect OS preference
onMounted(() => {
  // First check if theme preference exists in localStorage
  const savedTheme = localStorage.getItem('theme')

  if (savedTheme) {
    // Apply saved preference
    console.log('Found saved theme:', savedTheme) // Debug log
    isDarkMode.value = savedTheme === 'dark'
  } else {
    // Check system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    console.log('System prefers dark:', prefersDark) // Debug log
    isDarkMode.value = prefersDark
  }

  // Apply theme on initial load
  applyTheme()

  // Listen for OS theme changes if no preference is saved
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  mediaQuery.addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
      console.log('System theme changed:', e.matches ? 'dark' : 'light') // Debug log
      isDarkMode.value = e.matches
      applyTheme()
    }
  })

  // Force apply theme again after a slight delay to ensure it's applied
  setTimeout(() => {
    applyTheme()
    console.log('Theme applied after delay:', isDarkMode.value ? 'dark' : 'light') // Debug log
  }, 100)

  // Add a class to the document to indicate transitions should be enabled
  // We add this after a delay to prevent transitions on initial page load
  setTimeout(() => {
    document.documentElement.classList.add('theme-transitions-enabled')
  }, 500)
})

// Watch for changes to isDarkMode and apply them
watch(isDarkMode, (newValue) => {
  console.log('isDarkMode changed:', newValue) // Debug log
  applyTheme()
})
</script>

<template>
  <div :class="{ dark: isDarkMode }">
    <Sidebar
      variant="floating"
      collapsible="icon"
      class="bg-background text-foreground transition-colors"
    >
      <SidebarContent>
        <SidebarGroup>
          <div class="text-sm italic mb-4 transition-colors duration-300">
            <img src="@/assets/vestra.svg" alt="Vestra" class="h-16 w-16" />
          </div>
          <SidebarGroupContent>
            <SidebarMenu
              :class="[
                'flex flex-col gap-2',
                { 'items-center': state === 'collapsed' && !isMobile },
              ]"
            >
              <SidebarMenuItem v-for="item in items" :key="item.title">
                <SidebarMenuButton asChild>
                  <a
                    :href="item.url"
                    class="flex items-center gap-2 px-2 py-2 rounded-md hover:bg-copper/10 transition-all duration-300"
                  >
                    <component
                      :is="item.icon"
                      class="h-5 w-5 text-copper transition-colors duration-300 self-center"
                    />
                    <span class="transition-colors duration-300 text-sm">{{ item.title }}</span>
                  </a>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter class="border-t border-copper/30 pt-4 mt-auto transition-colors duration-300">
        <div
          class="flex flex-col space-y-4"
          :class="{
            'px-3': state === 'expanded' || isMobile,
            'px-1 items-center': state === 'collapsed' && !isMobile,
          }"
        >
          <!-- Theme Toggle -->
          <div
            class="flex items-center"
            :class="{
              'justify-between w-full': state === 'expanded' || isMobile,
              'justify-center': state === 'collapsed' && !isMobile,
            }"
          >
            <span
              v-if="state === 'expanded' || isMobile"
              class="text-sm transition-colors duration-300"
              >Theme</span
            >
            <div class="flex items-center" :class="{ 'gap-2': state === 'expanded' || isMobile }">
              <button
                v-if="state === 'collapsed' && !isMobile"
                @click="toggleTheme"
                class="flex items-center justify-center transition-colors duration-300"
              >
                <Sun
                  v-if="!isDarkMode"
                  class="h-4 w-4 text-copper transition-colors duration-300"
                />
                <Moon v-else class="h-4 w-4 text-copper transition-colors duration-300" />
              </button>
              <template v-else>
                <Sun
                  v-if="!isDarkMode"
                  class="h-4 w-4 text-copper transition-colors duration-300"
                />
                <Moon v-else class="h-4 w-4 text-copper transition-colors duration-300" />
                <Switch :modelValue="isDarkMode" @update:modelValue="toggleTheme" />
              </template>
            </div>
          </div>

          <!-- User Profile -->
          <DropdownMenu>
            <DropdownMenuTrigger
              class="flex items-center rounded-md hover:bg-copper/10 cursor-pointer transition-colors duration-300"
              :class="{
                'justify-between p-2 w-full': state === 'expanded' || isMobile,
                'justify-center p-1': state === 'collapsed' && !isMobile,
              }"
            >
              <div class="flex items-center gap-2">
                <div
                  class="h-8 w-8 rounded-full bg-copper flex items-center justify-center text-pale_white transition-colors duration-300"
                >
                  {{ username.charAt(0) }}
                </div>
                <span
                  v-if="state === 'expanded' || isMobile"
                  class="font-medium transition-colors duration-300"
                  >{{ username }}</span
                >
              </div>
              <ChevronUp
                v-if="state === 'expanded' || isMobile"
                class="h-4 w-4 transition-transform duration-300"
                :class="{ 'rotate-180': !isProfileOpen }"
              />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" class="w-56 transition-colors duration-300">
              <DropdownMenuItem class="cursor-pointer transition-colors duration-300">
                <User class="mr-2 h-4 w-4 transition-colors duration-300" />
                <span class="transition-colors duration-300">Account</span>
              </DropdownMenuItem>
              <DropdownMenuItem class="cursor-pointer transition-colors duration-300">
                <Settings class="mr-2 h-4 w-4 transition-colors duration-300" />
                <span class="transition-colors duration-300">Settings</span>
              </DropdownMenuItem>
              <DropdownMenuItem class="cursor-pointer text-red-500 transition-colors duration-300">
                <LogOut class="mr-2 h-4 w-4 transition-colors duration-300" />
                <span class="transition-colors duration-300">Sign out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </SidebarFooter>
    </Sidebar>
  </div>
</template>

<style>
/* Apply transitions to root theme changes */
html.theme-transitions-enabled * {
  transition-property:
    color, background-color, border-color, text-decoration-color, fill, stroke, opacity, box-shadow;
  transition-duration: var(--transition-duration);
  transition-timing-function: ease;
}

/* Prevent transitions on page load */
.theme-transitions-enabled {
  transition-property:
    color, background-color, border-color, text-decoration-color, fill, stroke, opacity, box-shadow;
  transition-duration: var(--transition-duration);
  transition-timing-function: ease;
}
</style>
