<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { Line } from 'vue-chartjs'

const props = defineProps<{
  stockSymbol: string
}>()

const chartData = ref<{ date: string; price: number }[]>([])
const predictionData = ref<{ date: string; price: number }[]>([])
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
        pointRadius: 3,
        pointHoverRadius: 8,
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
        pointRadius: 3,
        pointHoverRadius: 8,
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
      },
    },
  }
})

// Function to get prediction info from mock data
const getPredictionInfo = (symbol: string) => {
  // This is a simplified version - in a real app you'd get this from an API or store
  const predictionMap: { [key: string]: { direction: string; prediction: number } } = {
    AAPL: { direction: 'increase', prediction: 10 },
    MSFT: { direction: 'increase', prediction: 6 },
    AMZN: { direction: 'increase', prediction: 8 },
    TSLA: { direction: 'decrease', prediction: 12 },
  }

  return predictionMap[symbol] || { direction: 'increase', prediction: 5 }
}

// Function to fetch stock chart data
const fetchChartData = async (symbol: string) => {
  isLoading.value = true
  try {
    // In a real application, this would be an API call
    // For now, we'll use mock data
    await new Promise((resolve) => setTimeout(resolve, 500))

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
    // Get the last historical price as a starting point
    const lastPrice = mockData[mockData.length - 1].price

    // Use the predictions data from your StockPredictionList component
    // to determine the prediction trend
    const predictionInfo = getPredictionInfo(symbol)
    const direction = predictionInfo.direction === 'increase' ? 1 : -1
    const predictionPercent = predictionInfo.prediction / 100

    for (let i = 1; i <= 7; i++) {
      const date = new Date(today)
      date.setDate(date.getDate() + i)

      // Calculate predicted price with some randomness
      // The further into the future, the more the prediction percentage applies
      const progressFactor = i / 7
      const predictedChange = lastPrice * predictionPercent * progressFactor * direction
      const dailyRandomness = (Math.random() - 0.5) * 2

      predictionMockData.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        price: +(lastPrice + predictedChange + dailyRandomness).toFixed(2),
      })
    }
    predictionData.value = predictionMockData
  } catch (error) {
    console.error('Error fetching chart data:', error)
  } finally {
    isLoading.value = false
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
  fetchChartData(props.stockSymbol)
})
</script>

<template>
  <div class="h-full w-full">
    <div v-if="isLoading" class="h-full w-full flex items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-copper"></div>
    </div>
    <div v-else class="h-full w-full">
      <Line :data="chartDataset" :options="chartOptions" />
    </div>
  </div>
</template>
