<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { Line } from 'vue-chartjs'

const props = defineProps<{
  stockSymbol: string
}>()

const chartData = ref<{ date: string; price: number }[]>([])
const predictionData = ref<{ date: string; price: number }[]>([])
const upperBoundData = ref<{ date: string; price: number }[]>([])
const lowerBoundData = ref<{ date: string; price: number }[]>([])
const stockInfo = ref<any>(null)
const isLoading = ref(true)

// Computed properties for chart data structure
const chartDataset = computed(() => {
  return {
    labels: [
      ...chartData.value.map((item) => item.date),
      ...predictionData.value.map((item) => item.date),
    ],
    datasets: [
      {
        label: `${props.stockSymbol} Historical Price`,
        data: [
          ...chartData.value.map((item) => item.price),
          ...Array(predictionData.value.length).fill(null),
        ],
        borderColor: '#c87941',
        backgroundColor: 'rgba(200, 121, 65, 0.1)',
        borderWidth: 2,
        pointRadius: 2,
        pointHoverRadius: 6,
        tension: 0.4,
      },
      {
        label: `${props.stockSymbol} Predicted Price`,
        data: [
          ...Array(chartData.value.length).fill(null),
          ...predictionData.value.map((item) => item.price),
        ],
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        borderWidth: 2,
        borderDash: [5, 5],
        pointRadius: 2,
        pointHoverRadius: 6,
        tension: 0.4,
      },
      {
        label: 'Upper Bound',
        data: [
          ...Array(chartData.value.length).fill(null),
          ...upperBoundData.value.map((item) => item.price),
        ],
        borderColor: 'rgba(76, 175, 80, 0.3)',
        backgroundColor: 'transparent',
        borderWidth: 1,
        borderDash: [2, 2],
        pointRadius: 0,
        fill: false,
        tension: 0.4,
      },
      {
        label: 'Lower Bound',
        data: [
          ...Array(chartData.value.length).fill(null),
          ...lowerBoundData.value.map((item) => item.price),
        ],
        borderColor: 'rgba(200, 121, 65, 0.3)',
        backgroundColor: 'transparent',
        borderWidth: 1,
        borderDash: [2, 2],
        pointRadius: 0,
        fill: false,
        tension: 0.4,
      },
    ],
  }
})

const chartOptions = computed(() => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: false,
        grid: {
          color: 'rgba(136, 136, 136, 0.2)',
          drawBorder: false,
        },
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          // Display fewer x-axis labels for cleaner look
          maxTicksLimit: 10,
        },
      },
    },
    plugins: {
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        padding: 10,
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: '#c87941',
        borderWidth: 1,
        callbacks: {
          label: (context: any) => `$${context.parsed.y?.toFixed(2) || 'N/A'}`,
        },
      },
      legend: {
        display: true,
        position: 'top',
        labels: {
          // Hide the upper and lower bound labels
          filter: (legendItem: any) => {
            return !['Upper Bound', 'Lower Bound'].includes(legendItem.text)
          },
        },
      },
    },
  }
})

// Function to fetch stock chart data
const fetchChartData = async (symbol: string) => {
  isLoading.value = true
  try {
    // Direct path to the AAPL_data.json file
    const response = await fetch(`/stock_data/${symbol}_data.json`)
    if (!response.ok) {
      throw new Error(`Failed to fetch data for ${symbol}`)
    }

    const data = await response.json()

    // Set the chart data
    chartData.value = data.historical_data
    predictionData.value = data.prediction.data
    upperBoundData.value = data.prediction.upper_bound
    lowerBoundData.value = data.prediction.lower_bound
    stockInfo.value = {
      name: data.name,
      sentiment: data.sentiment,
    }
  } catch (error) {
    console.error('Error fetching chart data:', error)
    // Fall back to mock data if real data isn't available
    generateMockData(symbol)
  } finally {
    isLoading.value = false
  }
}

// Fallback to generate mock data if API call fails
const generateMockData = (symbol: string) => {
  // Generate mock data for the chart
  const mockData = []
  const today = new Date()
  for (let i = 30; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    // Base value with some realistic fluctuations
    const baseValue = symbol === 'AAPL' ? 175 : 160
    const randomFactor = Math.sin(i / 3) * 10 + (Math.random() - 0.5) * 8
    mockData.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      price: +(baseValue + randomFactor).toFixed(2),
    })
  }
  chartData.value = mockData

  // Generate prediction data for the next 7 days
  const predictionMockData = []
  const upperBoundMockData = []
  const lowerBoundMockData = []

  // Get the last historical price as a starting point
  const lastPrice = mockData[mockData.length - 1].price

  // Mock sentiment direction (positive or negative)
  const direction = Math.random() > 0.5 ? 1 : -1
  const predictionPercent = 0.05 // 5% change

  for (let i = 1; i <= 7; i++) {
    const date = new Date(today)
    date.setDate(date.getDate() + i)

    // Calculate predicted price with some randomness
    const progressFactor = i / 7
    const predictedChange = lastPrice * predictionPercent * progressFactor * direction
    const dailyRandomness = (Math.random() - 0.5) * 2
    const predictedPrice = +(lastPrice + predictedChange + dailyRandomness).toFixed(2)

    predictionMockData.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      price: predictedPrice,
    })

    upperBoundMockData.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      price: +(predictedPrice * 1.05).toFixed(2), // 5% above prediction
    })

    lowerBoundMockData.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      price: +(predictedPrice * 0.95).toFixed(2), // 5% below prediction
    })
  }

  predictionData.value = predictionMockData
  upperBoundData.value = upperBoundMockData
  lowerBoundData.value = lowerBoundMockData

  stockInfo.value = {
    name: symbol,
    sentiment: {
      score: direction * 0.2,
      category: direction > 0 ? 'Bullish' : 'Bearish',
      investment_score: 50 + direction * 10,
    },
  }
}

// Watch for changes in props.stockSymbol
watch(
  () => props.stockSymbol,
  (newSymbol) => {
    fetchChartData(newSymbol)
  },
)

onMounted(() => {
  // Initialize with AAPL data
  fetchChartData('AAPL')
})
</script>

<template>
  <div class="h-full w-full">
    <div v-if="isLoading" class="h-full w-full flex items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-copper"></div>
    </div>
    <div v-else class="h-full w-full">
      <div v-if="stockInfo" class="mb-4">
        <h3 class="text-lg font-bold">{{ stockInfo.name }} ({{ props.stockSymbol }})</h3>
        <div class="flex items-center mt-1">
          <span class="font-medium mr-2">Sentiment:</span>
          <span
            :class="{
              'text-green-500': stockInfo.sentiment.category === 'Bullish',
              'text-red-500': stockInfo.sentiment.category === 'Bearish',
              'text-gray-500': stockInfo.sentiment.category === 'Neutral',
            }"
          >
            {{ stockInfo.sentiment.category }}
            ({{ stockInfo.sentiment.score.toFixed(2) }})
          </span>
          <span class="ml-4 font-medium">Investment Score:</span>
          <span class="ml-1 font-bold"
            >{{ stockInfo.sentiment.investment_score.toFixed(1) }}/100</span
          >
        </div>
      </div>
      <Line :data="chartDataset" :options="chartOptions" />
    </div>
  </div>
</template>
