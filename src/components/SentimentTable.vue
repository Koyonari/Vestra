<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { TrendingUp, TrendingDown, ArrowUpDown, ChevronDown, ChevronUp } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import type { SentimentItem } from '@/types/sentiment'
import Papa from 'papaparse'

const sentimentData = ref<SentimentItem[]>([])
const isLoading = ref(true)
const sortColumn = ref<keyof SentimentItem>('rank')
const sortDirection = ref<'asc' | 'desc'>('asc')
const expanded = ref(false)
const initialDisplayCount = 10

const loadCsvData = async () => {
  try {
    const response = await fetch('/backend/reports/investment_ranking.csv')
    const csvText = await response.text()

    const results = Papa.parse(csvText, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
    })

    sentimentData.value = results.data as SentimentItem[]
  } catch (error) {
    console.error('Error loading CSV:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadCsvData()
})

// Another round of sorting just in case the data is not sorted correctly
const sortData = (column: keyof SentimentItem) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortDirection.value = 'asc'
  }

  sentimentData.value.sort((a, b) => {
    const multiplier = sortDirection.value === 'asc' ? 1 : -1
    return (a[column] < b[column] ? -1 : 1) * multiplier
  })
}

const displayedData = computed(() => {
  return expanded.value ? sentimentData.value : sentimentData.value.slice(0, initialDisplayCount)
})

const toggleExpand = () => {
  expanded.value = !expanded.value
}
</script>

<template>
  <div class="w-full">
    <div v-if="isLoading" class="flex justify-center items-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
    </div>

    <div v-else class="rounded-md border">
      <div class="relative w-full overflow-auto">
        <table class="w-full caption-bottom text-sm">
          <thead class="[&_tr]:border-b">
            <tr class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
              <th
                v-for="header in [
                  'Rank',
                  'Symbol',
                  'Company',
                  'Sentiment Score',
                  'Sentiment',
                  'Articles',
                ]"
                :key="header"
                class="h-12 px-4 text-left align-middle font-medium text-muted-foreground"
              >
                <div
                  class="flex items-center space-x-2"
                  @click="sortData(header.toLowerCase() as keyof SentimentItem)"
                >
                  <span>{{ header }}</span>
                  <ArrowUpDown class="h-4 w-4" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody class="[&_tr:last-child]:border-0">
            <tr
              v-for="item in displayedData"
              :key="item.ticker"
              class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted"
            >
              <td class="p-4 align-middle">{{ item.rank }}</td>
              <td class="p-4 align-middle font-medium">{{ item.ticker }}</td>
              <td class="p-4 align-middle">{{ item.name }}</td>
              <td class="p-4 align-middle">
                <div class="flex items-center gap-2">
                  <div class="w-24 bg-secondary rounded-full h-2">
                    <div
                      class="bg-primary h-2 rounded-full"
                      :style="{ width: `${item.investment_score}%` }"
                    />
                  </div>
                  <span>{{ item.investment_score.toFixed(1) }}</span>
                </div>
              </td>
              <td class="p-4 align-middle">
                <div class="flex items-center gap-2">
                  <TrendingUp v-if="item.avg_sentiment > 0" class="h-4 w-4 text-green-500" />
                  <TrendingDown v-else class="h-4 w-4 text-red-500" />
                  <span :class="item.avg_sentiment > 0 ? 'text-green-500' : 'text-red-500'">
                    {{ (item.avg_sentiment * 100).toFixed(2) }}%
                  </span>
                </div>
              </td>
              <td class="p-4 align-middle">{{ item.news_count }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="flex justify-center p-4">
        <Button variant="outline" @click="toggleExpand">
          {{ expanded ? 'Show Less' : `Show ${sentimentData.length - initialDisplayCount} More` }}
          <ChevronDown v-if="!expanded" class="h-4 w-4 ml-2" />
          <ChevronUp v-else class="h-4 w-4 ml-2" />
        </Button>
      </div>
    </div>
  </div>
</template>
