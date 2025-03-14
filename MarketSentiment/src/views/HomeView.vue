<script setup lang="ts">
import { ref, onMounted, watchEffect } from 'vue'
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

// Fetch stock data function
const fetchStockData = async (symbol: string) => {
  isLoading.value = true
  try {
    const response = await fetch(`/stock_data/${symbol}_data.json`)
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
      currentPrice: lastPrice,
      change: change,
      changePercent: changePercent,
      sentiment: data.sentiment,
    }
  } catch (error) {
    console.error('Error fetching stock data:', error)
    // Provide fallback data
    stockData.value = {
      name: symbol === 'AAPL' ? 'Apple Inc.' : symbol,
      currentPrice: 212.34,
      change: -3.3,
      changePercent: -1.53,
      sentiment: {
        category: 'Neutral',
        score: 0.0,
        investment_score: 50,
      },
    }
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
  // You could implement additional logic here to adjust chart data based on timeframe
}

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

    <!-- Bento Grid Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
      <!-- Stock Chart Card (Left Side - 2/3 width on large screens) -->
      <Card class="lg:col-span-2 bg-background shadow-md">
        <CardHeader class="pb-2">
          <div class="flex justify-between items-center">
            <div>
              <CardTitle class="text-xl font-bold">{{ selectedStock }} Stock Chart</CardTitle>
              <CardDescription v-if="stockData" class="flex items-center gap-2">
                <span>{{ stockData.name }}</span>
                <span class="font-semibold">${{ formatPrice(stockData.currentPrice) }}</span>
                <span
                  :class="stockData.change > 0 ? 'text-green-500' : 'text-red-500'"
                  class="flex items-center text-sm"
                >
                  <TrendingUp v-if="stockData.change > 0" class="h-4 w-4 mr-1" />
                  <TrendingDown v-else class="h-4 w-4 mr-1" />
                  {{ stockData.change > 0 ? '+' : '' }}{{ stockData.change.toFixed(2) }} ({{
                    stockData.change > 0 ? '+' : ''
                  }}{{ stockData.changePercent.toFixed(2) }}%)
                </span>
              </CardDescription>
            </div>
            <Tabs defaultValue="1M" class="w-auto" @update:value="handleTimeframeChange">
              <TabsList>
                <TabsTrigger value="1D">1D</TabsTrigger>
                <TabsTrigger value="1W">1W</TabsTrigger>
                <TabsTrigger value="1M">1M</TabsTrigger>
                <TabsTrigger value="3M">3M</TabsTrigger>
                <TabsTrigger value="1Y">1Y</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </CardHeader>
        <CardContent>
          <div class="h-64 w-full">
            <StockChart v-if="!isLoading" :stock-symbol="selectedStock" />
            <div v-else class="h-full w-full flex items-center justify-center">
              <div
                class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-copper"
              ></div>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Stock Predictions Card (Right Side - 1/3 width on large screens) -->
      <Card class="bg-background shadow-md">
        <CardHeader>
          <CardTitle class="text-xl font-bold flex items-center gap-2">
            <LineChart class="h-5 w-5 text-copper" />
            Stock Predictions
          </CardTitle>
          <CardDescription>Latest AI-powered market predictions</CardDescription>
        </CardHeader>
        <CardContent>
          <StockPredictionList />
        </CardContent>
      </Card>
    </div>

    <!-- Sentiment Score Table (Bottom) -->
    <Card class="mt-4 bg-background shadow-md">
      <CardHeader>
        <div class="flex items-center gap-2">
          <TrendingUp class="h-5 w-5 text-copper" />
          <CardTitle class="text-xl font-bold">Top 100 Sentiment Stocks</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <SentimentTable />
      </CardContent>
    </Card>
  </div>
</template>
