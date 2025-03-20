<script setup lang="ts">
import { ref, onMounted, computed, watchEffect } from 'vue'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { TrendingUp, TrendingDown, LineChart } from 'lucide-vue-next'
import StockChart from '@/components/StockChart.vue'
import StockPredictionList from '@/components/StockPredictionList.vue'
import SentimentTable from '@/components/SentimentTable.vue'

// State variables
const selectedStock = ref('AAPL')
const isLoading = ref(true)
const stockData = ref<any>(null)
const selectedTimeframe = ref('1M')
const currentPrice = ref(0)

// Fetch stock data function
const fetchStockData = async (symbol: string) => {
  isLoading.value = true
  try {
    // Since API is not ready, directly use the local JSON files
    const response = await fetch(`/backend/stock_data/${symbol}_data.json`)

    if (!response.ok) {
      throw new Error(`Failed to fetch data for ${symbol}`)
    }

    const data = await response.json()

    // Calculate the current price (last historical price)
    const historicalData = data.historical_data
    const lastPrice = historicalData[historicalData.length - 1].price
    const prevPrice = historicalData[historicalData.length - 2].price
    const change = lastPrice - prevPrice
    const changePercent = (change / prevPrice) * 100

    stockData.value = {
      name: data.name,
      ticker: data.ticker,
      currentPrice: lastPrice,
      change: change,
      changePercent: changePercent,
      sentiment: data.sentiment,
      historical_data: data.historical_data,
      prediction: data.prediction,
      last_updated: data.last_updated,
    }

    currentPrice.value = lastPrice
  } catch (error) {
    console.error('Error fetching stock data:', error)
  } finally {
    isLoading.value = false
  }
}

// Format price to ensure proper decimal display
const formatPrice = (price: number) => {
  return price.toFixed(2)
}

// Handle timeframe change
const handleTimeframeChange = (timeframe: string) => {
  selectedTimeframe.value = timeframe
}

// Handle chart loaded event
const handleChartLoaded = (data: any) => {
  stockData.value = {
    ...stockData.value,
    ...data,
  }
  currentPrice.value = data.currentPrice
  isLoading.value = false
}

const priceChange = computed(() => {
  if (!stockData.value || !stockData.value.historical_data?.length) {
    return { value: 0, percent: 0 }
  }

  const historicalData = stockData.value.historical_data
  const currentPrice = historicalData[historicalData.length - 1].price
  const previousPrice = historicalData[historicalData.length - 2]?.price || currentPrice
  const change = currentPrice - previousPrice
  const percentChange = (change / previousPrice) * 100

  return {
    value: change.toFixed(2),
    percent: percentChange.toFixed(2),
  }
})

// Compute the sentiment score indicator position (for sentiment display in right panel)
const sentimentPosition = computed(() => {
  if (!stockData.value || !stockData.value.sentiment) return '50%'
  // Normalize the score to a percentage (0-100)
  // Assuming score ranges from -1 to 1
  const normalizedScore = ((stockData.value.sentiment.score + 1) / 2) * 100
  return `${normalizedScore}%`
})

// Compute the investment score indicator position (for sentiment display in right panel)
const investmentPosition = computed(() => {
  if (!stockData.value || !stockData.value.sentiment) return '50%'
  // Assuming investment_score is already 0-100
  return `${stockData.value.sentiment.investment_score}%`
})

// Compute sentiment category color (for sentiment display in right panel)
const categoryColor = computed(() => {
  if (!stockData.value || !stockData.value.sentiment) return 'text-yellow-500'
  const category = stockData.value.sentiment.category.toLowerCase()
  if (category.includes('bullish')) return 'text-green-500'
  if (category.includes('bearish')) return 'text-red-500'
  return 'text-yellow-500' // Neutral
})

// Get the last prediction date and price (for prediction display in right panel)
const lastPrediction = computed(() => {
  if (
    !stockData.value ||
    !stockData.value.prediction ||
    !stockData.value.prediction.data ||
    stockData.value.prediction.data.length === 0
  ) {
    return { date: '', price: 0 }
  }

  const lastIndex = stockData.value.prediction.data.length - 1
  return {
    date: new Date(stockData.value.prediction.data[lastIndex].date).toLocaleDateString(),
    price: stockData.value.prediction.data[lastIndex].price,
  }
})

// Calculate the prediction change percentage (for prediction display in right panel)
const predictionChange = computed(() => {
  if (!stockData.value || !lastPrediction.value.price || !stockData.value.currentPrice) {
    return { value: '0.00', percent: '0.00' }
  }

  const change = lastPrediction.value.price - stockData.value.currentPrice
  const percentChange = (change / stockData.value.currentPrice) * 100
  return {
    value: change.toFixed(2),
    percent: percentChange.toFixed(2),
  }
})

// Calculate the upper and lower bounds (for prediction display in right panel)
const bounds = computed(() => {
  if (
    !stockData.value ||
    !stockData.value.prediction ||
    !stockData.value.prediction.upper_bound ||
    !stockData.value.prediction.lower_bound ||
    stockData.value.prediction.upper_bound.length === 0 ||
    stockData.value.prediction.lower_bound.length === 0
  ) {
    return { upper: '0.00', lower: '0.00' }
  }

  const lastIndex = stockData.value.prediction.upper_bound.length - 1
  return {
    upper: stockData.value.prediction.upper_bound[lastIndex].price.toFixed(2),
    lower: stockData.value.prediction.lower_bound[lastIndex].price.toFixed(2),
  }
})

// Determine if the prediction is positive or negative
const isPredictionPositive = computed(() => {
  if (!stockData.value || !lastPrediction.value.price || !stockData.value.currentPrice) {
    return false
  }
  return lastPrediction.value.price >= stockData.value.currentPrice
})

// Watch for changes in selected stock
watchEffect(() => {
  if (selectedStock.value) {
    fetchStockData(selectedStock.value)
  }
})

onMounted(() => {
  fetchStockData(selectedStock.value)
})
</script>

<template>
  <div class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6 text-copper dark:text-white">Vestra Dashboard</h1>
    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- Left Section (2/3 width) -->
      <div class="lg:col-span-2 flex flex-col space-y-4">
        <!-- Stock Chart Card -->
        <Card class="bg-background shadow-md flex-grow flex-col flex">
          <CardHeader class="pb-2">
            <div class="flex justify-between items-center">
              <div>
                <CardTitle class="text-xl font-bold">{{ selectedStock }} Stock Chart</CardTitle>
                <CardDescription v-if="stockData" class="flex items-center gap-2">
                  <span>{{ stockData.name }}</span>
                  <span class="font-semibold">${{ formatPrice(currentPrice) }}</span>
                  <span
                    :class="Number(priceChange.value) > 0 ? 'text-green-500' : 'text-red-500'"
                    class="flex items-center text-sm"
                  >
                    <TrendingUp v-if="Number(priceChange.value) > 0" class="h-4 w-4 mr-1" />
                    <TrendingDown v-else class="h-4 w-4 mr-1" />
                    {{ Number(priceChange.value) > 0 ? '+' : '' }}{{ priceChange.value }} ({{
                      priceChange.percent
                    }}%)
                  </span>
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent class="p-6">
            <div class="h-72 w-full flex items-center justify-center mb-4">
              <StockChart
                v-if="!isLoading"
                :stock-symbol="selectedStock"
                :timeframe="selectedTimeframe"
                @chart-loaded="handleChartLoaded"
                class="w-full"
              />
              <div v-else class="h-full w-full flex items-center justify-center">
                <div
                  class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-copper"
                ></div>
              </div>
            </div>
          </CardContent>
        </Card>
        <!-- Sentiment Analysis Card with flexible height -->
        <Card
          class="bg-background shadow-md flex-grow flex-col flex"
          v-if="stockData && stockData.sentiment"
        >
          <CardHeader>
            <CardTitle class="text-lg font-semibold">Sentiment Analysis</CardTitle>
          </CardHeader>
          <CardContent class="p-6 flex-grow flex flex-col justify-between">
            <!-- Sentiment Score -->
            <div class="space-y-6 flex-grow">
              <div class="space-y-3">
                <div class="flex justify-between text-sm">
                  <span>Bearish</span>
                  <span :class="categoryColor">{{ stockData.sentiment.category }}</span>
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
              <div class="space-y-3">
                <div class="flex justify-between text-sm">
                  <span>High Risk</span>
                  <span class="font-medium"
                    >Investment Score: {{ stockData.sentiment.investment_score }}/100</span
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
            <!-- Spacer div to push content to top -->
            <div class="mt-auto pt-4"></div>
          </CardContent>
        </Card>
      </div>

      <!-- Right Section (1/3 width) -->
      <div class="flex flex-col space-y-4 h-full">
        <!-- Price Prediction Card -->
        <Card
          class="bg-background shadow-md flex-grow flex"
          v-if="stockData && stockData.prediction"
        >
          <CardHeader>
            <CardTitle class="text-lg font-semibold">Price Prediction</CardTitle>
          </CardHeader>
          <CardContent class="p-4">
            <div class="space-y-4">
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-500">Current Price</span>
                <span class="font-medium" v-if="stockData"
                  >${{ stockData.currentPrice.toFixed(2) }}</span
                >
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-500"
                  >Predicted Price <br />({{ lastPrediction.date }})</span
                >
                <span class="font-medium">${{ lastPrediction.price.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-500"
                  >Prediction<br />
                  Change</span
                >
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

        <!-- Stock Predictions Card -->
        <Card class="bg-background shadow-md flex-col flex">
          <CardHeader>
            <CardTitle class="text-xl font-bold flex items-center gap-2">
              <LineChart class="h-5 w-5 text-copper" />
              Stock Predictions
            </CardTitle>
            <CardDescription>Latest AI-powered market predictions</CardDescription>
          </CardHeader>
          <CardContent class="p-4 flex-grow">
            <StockPredictionList class="h-full" />
          </CardContent>
        </Card>
      </div>
    </div>

    <!-- Sentiment Score Table (Bottom, Full Width) -->
    <Card class="mt-4 bg-background shadow-md">
      <CardHeader>
        <div class="flex items-center gap-2">
          <TrendingUp class="h-5 w-5 text-copper" />
          <CardTitle class="text-xl font-bold">Top 100 Sentiment Stocks</CardTitle>
        </div>
      </CardHeader>
      <CardContent class="p-4">
        <SentimentTable />
      </CardContent>
    </Card>
  </div>
</template>
