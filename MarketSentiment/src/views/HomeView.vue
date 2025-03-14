<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { LineChart, ChevronDown, ChevronUp, TrendingUp, TrendingDown } from 'lucide-vue-next'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../components/ui/collapsible'
import StockChart from '../components/StockChart.vue'
import StockPredictionList from '../components/StockPredictionList.vue'
import SentimentTable from '../components/SentimentTable.vue'

// Selected stock data
const selectedStock = ref('AAPL')
interface StockData {
  symbol: string
  name: string
  currentPrice: number
  change: number
  changePercent: number
}

const stockData = ref<StockData | null>(null)
const isLoading = ref(true)
const sentimentExpanded = ref(false)

// Fetch stock data function
const fetchStockData = async (symbol: string) => {
  isLoading.value = true
  try {
    // In a real application, this would be an API call
    // For now, we'll simulate loading
    await new Promise((resolve) => setTimeout(resolve, 1000))
    stockData.value = {
      symbol,
      name: symbol === 'AAPL' ? 'Apple Inc.' : symbol === 'AMZN' ? 'Amazon.com Inc.' : symbol,
      currentPrice: symbol === 'AAPL' ? 187.62 : 178.15,
      change: symbol === 'AAPL' ? 1.23 : 0.87,
      changePercent: symbol === 'AAPL' ? 0.66 : 0.49,
    }
  } catch (error) {
    console.error('Error fetching stock data:', error)
  } finally {
    isLoading.value = false
  }
}

// Toggle sentiment section
const toggleSentiment = () => {
  sentimentExpanded.value = !sentimentExpanded.value
}

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
                <span class="font-semibold">{{ stockData.currentPrice }}</span>
                <span
                  :class="stockData.change > 0 ? 'text-green-500' : 'text-red-500'"
                  class="flex items-center text-sm"
                >
                  <TrendingUp v-if="stockData.change > 0" class="h-4 w-4 mr-1" />
                  <TrendingDown v-else class="h-4 w-4 mr-1" />
                  {{ stockData.change > 0 ? '+' : '' }}{{ stockData.change }} ({{
                    stockData.change > 0 ? '+' : ''
                  }}{{ stockData.changePercent }}%)
                </span>
              </CardDescription>
            </div>
            <Tabs defaultValue="1M" class="w-auto">
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
