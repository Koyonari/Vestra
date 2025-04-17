<script setup lang="ts">
import { ref, onMounted, watch, computed, onBeforeUnmount } from 'vue'
import {
  createChart,
  ColorType,
  LineStyle,
  PriceScaleMode,
  LineSeries,
  AreaSeries,
} from 'lightweight-charts'

const props = defineProps<{
  stockSymbol: string
  timeframe: string
}>()

const emit = defineEmits(['chart-loaded'])

const chartData = ref<{ date: string; price: number }[]>([])
const predictionData = ref<{ date: string; price: number }[]>([])
const upperBoundData = ref<{ date: string; price: number }[]>([])
const lowerBoundData = ref<{ date: string; price: number }[]>([])
interface StockInfo {
  name: string
  sentiment: {
    score: number
    category: string
    investment_score: number
  }
  lastUpdated: string
}

const stockInfo = ref<StockInfo | null>(null)
const isLoading = ref(true)
const errorMessage = ref('')
const chartContainerRef = ref<HTMLElement | null>(null)
import type { IChartApi } from 'lightweight-charts'

const chart = ref<IChartApi | null>(null)
const resizeObserver = ref<ResizeObserver | null>(null)

// In the initializeChart function, update the chart creation:

const initializeChart = () => {
  if (!chartContainerRef.value) return

  // Clear previous chart if it exists
  if (chart.value) {
    chart.value.remove()
    chart.value = null
  }

  try {
    // Create new chart - make sure the DOM element is ready
    const container = chartContainerRef.value

    // Wait for the container to be properly rendered
    setTimeout(() => {
      // Ensure the container has dimensions
      if (container.clientWidth === 0 || container.clientHeight === 0) {
        console.error('Chart container has zero dimensions')
        container.style.height = '300px' // Force a height if none exists
        container.style.width = '100%' // Force a width if none exists
      }

      const chartOptions = {
        width: container.clientWidth || 800,
        height: container.clientHeight || 300,
        layout: {
          background: { type: ColorType.Solid, color: 'transparent' },
          textColor: '#d1d5db',
        },
        grid: {
          vertLines: { color: 'rgba(42, 46, 57, 0.2)', style: LineStyle.Dotted },
          horzLines: { color: 'rgba(42, 46, 57, 0.2)', style: LineStyle.Dotted },
        },
        rightPriceScale: {
          borderColor: 'rgba(197, 203, 206, 0.8)',
          mode: PriceScaleMode.Normal,
        },
        timeScale: {
          borderColor: 'rgba(197, 203, 206, 0.8)',
          timeVisible: true,
          fixLeftEdge: true,
          fixRightEdge: true,
          rightBarStaysOnScroll: true,
        },
        crosshair: {
          mode: 0, // CrosshairMode.Normal
        },
      }

      // Create the chart with explicit type
      chart.value = createChart(container, chartOptions)

      // Verify chart was created successfully
      if (!chart.value) {
        throw new Error('Failed to create chart instance')
      }

      // Add historical data series
      const mainSeries = chart.value.addSeries(AreaSeries, {
        lineColor: '#2962FF',
        topColor: '#2962FF',
        bottomColor: 'rgba(41, 98, 255, 0.28)',
        lineWidth: 2,
      })

      // Format data for the chart
      const formattedHistoricalData = chartData.value.map((item) => ({
        time: item.date,
        value: item.price,
      }))

      if (formattedHistoricalData.length > 0) {
        mainSeries.setData(formattedHistoricalData)
      } else {
        console.warn('No historical data available to display')
      }

      // Add prediction data if available
      if (predictionData.value.length > 0) {
        const predictionSeries = chart.value.addSeries(LineSeries, {
          color: '#FF9800',
          lineWidth: 2,
          lineStyle: LineStyle.Dashed,
        })

        const formattedPredictionData = predictionData.value.map((item) => ({
          time: item.date,
          value: item.price,
        }))

        predictionSeries.setData(formattedPredictionData)

        // Add upper bound
        if (upperBoundData.value.length > 0) {
          const upperBoundSeries = chart.value.addSeries(LineSeries, {
            color: 'rgba(76, 175, 80, 0.5)',
            lineWidth: 1,
            lineStyle: LineStyle.Dotted,
          })

          const formattedUpperBoundData = upperBoundData.value.map((item) => ({
            time: item.date,
            value: item.price,
          }))

          upperBoundSeries.setData(formattedUpperBoundData)
        }

        // Add lower bound
        if (lowerBoundData.value.length > 0) {
          const lowerBoundSeries = chart.value.addSeries(LineSeries, {
            color: 'rgba(244, 67, 54, 0.5)',
            lineWidth: 1,
            lineStyle: LineStyle.Dotted,
          })

          const formattedLowerBoundData = lowerBoundData.value.map((item) => ({
            time: item.date,
            value: item.price,
          }))

          lowerBoundSeries.setData(formattedLowerBoundData)
        }
      }

      // Fit content to view all data
      chart.value.timeScale().fitContent()
    }, 0)
  } catch (error) {
    console.error('Error initializing chart:', error)
    errorMessage.value = 'Failed to initialize chart. Please try again.'
  }
}
// Function to fetch stock chart data
const fetchChartData = async (symbol: string) => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    // Since API is not ready, directly use the local JSON files
    const response = await fetch(`/backend/stock_data/${symbol}_data.json`)

    if (response.ok) {
      const data = await response.json()

      // Ensure dates are in the correct format (YYYY-MM-DD)
      chartData.value = data.historical_data.map((item: { date: string; price: string }) => ({
        date: item.date,
        price: Number(item.price), // Ensure price is a number
      }))

      predictionData.value = data.prediction.data.map((item: { date: string; price: string }) => ({
        date: item.date,
        price: Number(item.price),
      }))

      upperBoundData.value = data.prediction.upper_bound.map(
        (item: { date: string; price: string }) => ({
          date: item.date,
          price: Number(item.price),
        }),
      )

      lowerBoundData.value = data.prediction.lower_bound.map(
        (item: { date: string; price: string }) => ({
          date: item.date,
          price: Number(item.price),
        }),
      )

      stockInfo.value = {
        name: data.name,
        sentiment: data.sentiment,
        lastUpdated: data.last_updated,
      }

      // Emit the data to the parent component
      emit('chart-loaded', {
        name: data.name,
        ticker: data.ticker,
        historical_data: data.historical_data,
        currentPrice: data.historical_data[data.historical_data.length - 1].price,
        sentiment: data.sentiment,
        last_updated: data.last_updated,
      })
    } else {
      // If file not found, use the generateMockDataFromJson function
      throw new Error(`Failed to fetch data for ${symbol}`)
    }
  } finally {
    // Initialize chart after data is loaded
    // Use setTimeout to ensure DOM is ready
    setTimeout(() => {
      initializeChart()
      isLoading.value = false
    }, 100)
  }
}
// Handle window resize
const handleResize = () => {
  if (chart.value && chartContainerRef.value) {
    chart.value.applyOptions({
      width: chartContainerRef.value.clientWidth,
    })
  }
}

// Watch for changes in stock symbol
watch(
  () => props.stockSymbol,
  (newSymbol) => {
    if (newSymbol) {
      fetchChartData(newSymbol)
    }
  },
)

onMounted(() => {
  // Wait for the DOM to be fully rendered
  setTimeout(() => {
    fetchChartData(props.stockSymbol)

    // Set up resize observer
    if (chartContainerRef.value) {
      resizeObserver.value = new ResizeObserver(handleResize)
      resizeObserver.value.observe(chartContainerRef.value)
    }

    // Add window resize event listener
    window.addEventListener('resize', handleResize)
  }, 100)
})

onBeforeUnmount(() => {
  // Clean up
  if (resizeObserver.value && chartContainerRef.value) {
    resizeObserver.value.unobserve(chartContainerRef.value)
  }

  window.removeEventListener('resize', handleResize)

  if (chart.value) {
    chart.value.remove()
  }
})
</script>

<template>
  <div class="relative w-full h-full">
    <div
      v-if="errorMessage"
      class="absolute top-0 left-0 bg-yellow-100 text-yellow-800 p-2 text-xs rounded"
    >
      {{ errorMessage }}
    </div>
    <div
      ref="chartContainerRef"
      class="w-full h-full"
      style="min-height: 300px; min-width: 300px"
    ></div>
  </div>
</template>
