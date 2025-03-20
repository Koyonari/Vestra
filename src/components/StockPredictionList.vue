<script setup lang="ts">
import { ref, computed } from 'vue'
import { TrendingUp, TrendingDown, ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'

const predictions = ref([
  {
    id: 1,
    company: 'Apple',
    symbol: 'AAPL',
    prediction: 10,
    direction: 'increase',
    timeframe: '7 days',
    timestamp: '2h ago',
    logoClass: 'bg-gray-200',
  },
  {
    id: 2,
    company: 'Apple',
    symbol: 'AAPL',
    prediction: 5,
    direction: 'decrease',
    timeframe: '7 days',
    timestamp: '1d ago',
    logoClass: 'bg-gray-200',
  },
  {
    id: 3,
    company: 'Amazon',
    symbol: 'AMZN',
    prediction: 8,
    direction: 'increase',
    timeframe: '7 days',
    timestamp: '2d ago',
    logoClass: 'bg-gray-100',
  },
  {
    id: 4,
    company: 'Microsoft',
    symbol: 'MSFT',
    prediction: 6,
    direction: 'increase',
    timeframe: '7 days',
    timestamp: '3d ago',
    logoClass: 'bg-green-100',
  },
  {
    id: 5,
    company: 'Tesla',
    symbol: 'TSLA',
    prediction: 12,
    direction: 'decrease',
    timeframe: '7 days',
    timestamp: '4d ago',
    logoClass: 'bg-red-100',
  },
])

// Pagination logic
const itemsPerPage = 3
const currentPage = ref(1)
const totalPages = computed(() => Math.ceil(predictions.value.length / itemsPerPage))

const paginatedPredictions = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return predictions.value.slice(start, end)
})

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}
</script>

<template>
  <div class="h-[360px] flex flex-col justify-between">
    <div class="space-y-4 overflow-y-auto">
      <div
        v-for="prediction in paginatedPredictions"
        :key="prediction.id"
        class="flex items-center gap-4 p-3 border-b border-copper/20 last:border-none"
      >
        <div
          :class="[prediction.logoClass, 'h-10 w-10 rounded-full flex items-center justify-center']"
        >
          <span class="text-sm font-semibold">{{ prediction.symbol.substring(0, 1) }}</span>
        </div>
        <div class="flex-1">
          <div class="flex items-center gap-2">
            <TrendingUp v-if="prediction.direction === 'increase'" class="h-4 w-4 text-green-500" />
            <TrendingDown v-else class="h-4 w-4 text-red-500" />
            <span class="font-medium">
              {{ prediction.company }} stock is predicted to
              <span
                :class="prediction.direction === 'increase' ? 'text-green-500' : 'text-red-500'"
              >
                {{ prediction.direction }}
              </span>
              by {{ prediction.prediction }}% in the next {{ prediction.timeframe }}
            </span>
          </div>
          <div class="text-xs text-gray-500 mt-1">
            {{ prediction.timestamp }}
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination Controls -->
    <div class="flex justify-between items-center mt-4 pt-2 border-t">
      <Button variant="outline" size="sm" :disabled="currentPage === 1" @click="prevPage">
        <ChevronLeft class="h-4 w-4" />
      </Button>

      <span class="text-sm"> Page {{ currentPage }} of {{ totalPages }} </span>

      <Button variant="outline" size="sm" :disabled="currentPage === totalPages" @click="nextPage">
        <ChevronRight class="h-4 w-4" />
      </Button>
    </div>
  </div>
</template>
