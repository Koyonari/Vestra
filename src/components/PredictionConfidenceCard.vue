<script setup lang="ts">
import { computed } from 'vue'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

const props = defineProps<{
  currentPrice: number
  prediction: {
    data: { date: string; price: number }[]
    upper_bound: { date: string; price: number }[]
    lower_bound: { date: string; price: number }[]
  }
}>()

// Get the last prediction date and price
const lastPrediction = computed(() => {
  const lastIndex = props.prediction.data.length - 1
  return {
    date: new Date(props.prediction.data[lastIndex].date).toLocaleDateString(),
    price: props.prediction.data[lastIndex].price,
  }
})

// Calculate the prediction change percentage
const predictionChange = computed(() => {
  const change = lastPrediction.value.price - props.currentPrice
  const percentChange = (change / props.currentPrice) * 100
  return {
    value: change.toFixed(2),
    percent: percentChange.toFixed(2),
  }
})

// Calculate the upper and lower bounds
const bounds = computed(() => {
  const lastIndex = props.prediction.upper_bound.length - 1
  return {
    upper: props.prediction.upper_bound[lastIndex].price.toFixed(2),
    lower: props.prediction.lower_bound[lastIndex].price.toFixed(2),
  }
})

// Determine if the prediction is positive or negative
const isPredictionPositive = computed(() => {
  return lastPrediction.value.price >= props.currentPrice
})
</script>

<template>
  <Card class="bg-background shadow-md">
    <CardHeader>
      <CardTitle class="text-lg font-semibold">Price Prediction</CardTitle>
    </CardHeader>
    <CardContent>
      <div class="space-y-4">
        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-500">Current Price</span>
          <span class="font-medium">${{ currentPrice.toFixed(2) }}</span>
        </div>

        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-500">Predicted Price ({{ lastPrediction.date }})</span>
          <span class="font-medium">${{ lastPrediction.price.toFixed(2) }}</span>
        </div>

        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-500">Prediction Change</span>
          <span
            :class="isPredictionPositive ? 'text-green-500' : 'text-red-500'"
            class="font-medium"
          >
            {{ isPredictionPositive ? '+' : '' }}{{ predictionChange.value }} ({{
              predictionChange.percent
            }}%)
          </span>
        </div>

        <div class="pt-2 border-t border-gray-200 dark:border-gray-700">
          <div class="text-sm text-gray-500 mb-2">Confidence Interval</div>
          <div class="flex justify-between items-center">
            <span class="text-sm">Lower Bound</span>
            <span class="font-medium">${{ bounds.lower }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm">Upper Bound</span>
            <span class="font-medium">${{ bounds.upper }}</span>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
</template>
