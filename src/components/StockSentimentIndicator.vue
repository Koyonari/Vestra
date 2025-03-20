<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  sentiment: {
    score: number
    category: string
    investment_score: number
  }
}>()

// Compute the sentiment score indicator position
const sentimentPosition = computed(() => {
  // Normalize the score to a percentage (0-100)
  // Assuming score ranges from -1 to 1
  const normalizedScore = ((props.sentiment.score + 1) / 2) * 100
  return `${normalizedScore}%`
})

// Compute the investment score indicator position
const investmentPosition = computed(() => {
  // Assuming investment_score is already 0-100
  return `${props.sentiment.investment_score}%`
})

// Compute sentiment category color
const categoryColor = computed(() => {
  const category = props.sentiment.category.toLowerCase()
  if (category.includes('bullish')) return 'text-green-500'
  if (category.includes('bearish')) return 'text-red-500'
  return 'text-yellow-500' // Neutral
})
</script>

<template>
  <div class="space-y-4 p-4 bg-white dark:bg-gray-900 rounded-lg shadow-md">
    <h3 class="text-lg font-semibold mb-2">Sentiment Analysis</h3>

    <!-- Sentiment Score -->
    <div class="space-y-2">
      <div class="flex justify-between text-sm">
        <span>Bearish</span>
        <span :class="categoryColor">{{ props.sentiment.category }}</span>
        <span>Bullish</span>
      </div>
      <div class="relative h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
        <div class="absolute w-full h-full flex items-center justify-center">
          <div
            class="absolute h-4 w-4 rounded-full bg-blue-500 shadow-md z-10"
            :style="{ left: sentimentPosition }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Investment Score -->
    <div class="space-y-2">
      <div class="flex justify-between text-sm">
        <span>High Risk</span>
        <span class="font-medium"
          >Investment Score: {{ props.sentiment.investment_score }}/100</span
        >
        <span>Low Risk</span>
      </div>
      <div class="relative h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
        <div
          class="absolute h-full bg-gradient-to-r from-red-500 via-yellow-400 to-green-500 rounded-full"
          style="width: 100%"
        ></div>
        <div class="absolute w-full h-full flex items-center justify-center">
          <div
            class="absolute h-4 w-4 rounded-full bg-white border-2 border-blue-500 shadow-md z-10"
            :style="{ left: investmentPosition }"
          ></div>
        </div>
      </div>
    </div>
  </div>
</template>
