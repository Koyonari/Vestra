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
const stockInfo = ref<any>(null)
const isLoading = ref(true)
const errorMessage = ref('')
const chartContainerRef = ref<HTMLElement | null>(null)
const chart = ref<any>(null)
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
      chartData.value = data.historical_data.map((item: any) => ({
        date: item.date,
        price: Number(item.price), // Ensure price is a number
      }))

      predictionData.value = data.prediction.data.map((item: any) => ({
        date: item.date,
        price: Number(item.price),
      }))

      upperBoundData.value = data.prediction.upper_bound.map((item: any) => ({
        date: item.date,
        price: Number(item.price),
      }))

      lowerBoundData.value = data.prediction.lower_bound.map((item: any) => ({
        date: item.date,
        price: Number(item.price),
      }))

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
  } catch (error) {
    console.error('Error fetching chart data:', error)
    errorMessage.value = `Using local data for ${symbol}.`
    // Fall back to mock data if real data isn't available
    generateMockDataFromJson(symbol)
  } finally {
    // Initialize chart after data is loaded
    // Use setTimeout to ensure DOM is ready
    setTimeout(() => {
      initializeChart()
      isLoading.value = false
    }, 100)
  }
}

// Use the JSON data provided
const generateMockDataFromJson = (symbol: string) => {
  if (symbol === 'AAPL') {
    const data = {
      ticker: 'AAPL',
      name: 'Apple Inc.',
      sentiment: {
        score: 0.09,
        category: 'Bullish',
        investment_score: 58.9,
      },
      historical_data: [
        { date: '2024-12-16', price: 250.76 },
        { date: '2024-12-17', price: 253.2 },
        { date: '2024-12-18', price: 247.78 },
        { date: '2024-12-19', price: 249.52 },
        { date: '2024-12-20', price: 254.21 },
        { date: '2024-12-23', price: 254.99 },
        { date: '2024-12-24', price: 257.92 },
        { date: '2024-12-26', price: 258.74 },
        { date: '2024-12-27', price: 255.31 },
        { date: '2024-12-30', price: 251.92 },
        { date: '2024-12-31', price: 250.14 },
        { date: '2025-01-02', price: 243.58 },
        { date: '2025-01-03', price: 243.09 },
        { date: '2025-01-06', price: 244.73 },
        { date: '2025-01-07', price: 241.94 },
        { date: '2025-01-08', price: 242.43 },
        { date: '2025-01-10', price: 236.59 },
        { date: '2025-01-13', price: 234.14 },
        { date: '2025-01-14', price: 233.02 },
        { date: '2025-01-15', price: 237.61 },
        { date: '2025-01-16', price: 228.01 },
        { date: '2025-01-17', price: 229.73 },
        { date: '2025-01-21', price: 222.4 },
        { date: '2025-01-22', price: 223.58 },
        { date: '2025-01-23', price: 223.41 },
        { date: '2025-01-24', price: 222.54 },
        { date: '2025-01-27', price: 229.61 },
        { date: '2025-01-28', price: 238.0 },
        { date: '2025-01-29', price: 239.1 },
        { date: '2025-01-30', price: 237.33 },
        { date: '2025-01-31', price: 235.74 },
        { date: '2025-02-03', price: 227.76 },
        { date: '2025-02-04', price: 232.54 },
        { date: '2025-02-05', price: 232.21 },
        { date: '2025-02-06', price: 232.96 },
        { date: '2025-02-07', price: 227.38 },
        { date: '2025-02-10', price: 227.65 },
        { date: '2025-02-11', price: 232.62 },
        { date: '2025-02-12', price: 236.87 },
        { date: '2025-02-13', price: 241.53 },
        { date: '2025-02-14', price: 244.6 },
        { date: '2025-02-18', price: 244.47 },
        { date: '2025-02-19', price: 244.87 },
        { date: '2025-02-20', price: 245.83 },
        { date: '2025-02-21', price: 245.55 },
        { date: '2025-02-24', price: 247.1 },
        { date: '2025-02-25', price: 247.04 },
        { date: '2025-02-26', price: 240.36 },
        { date: '2025-02-27', price: 237.3 },
        { date: '2025-02-28', price: 241.84 },
        { date: '2025-03-03', price: 238.03 },
        { date: '2025-03-04', price: 235.93 },
        { date: '2025-03-05', price: 235.74 },
        { date: '2025-03-06', price: 235.33 },
        { date: '2025-03-07', price: 239.07 },
        { date: '2025-03-10', price: 227.48 },
        { date: '2025-03-11', price: 220.84 },
        { date: '2025-03-12', price: 216.98 },
        { date: '2025-03-13', price: 209.68 },
        { date: '2025-03-14', price: 212.34 },
      ],
      prediction: {
        data: [
          { date: '2025-03-15', price: 212.34 },
          { date: '2025-03-16', price: 212.38 },
          { date: '2025-03-17', price: 210.1 },
          { date: '2025-03-18', price: 210.13 },
          { date: '2025-03-19', price: 208.91 },
          { date: '2025-03-20', price: 208.28 },
          { date: '2025-03-21', price: 206.77 },
          { date: '2025-03-22', price: 204.73 },
          { date: '2025-03-23', price: 204.09 },
          { date: '2025-03-24', price: 204.43 },
          { date: '2025-03-25', price: 201.13 },
          { date: '2025-03-26', price: 200.28 },
          { date: '2025-03-27', price: 198.78 },
          { date: '2025-03-28', price: 196.58 },
          { date: '2025-03-29', price: 195.35 },
          { date: '2025-03-30', price: 195.43 },
          { date: '2025-03-31', price: 194.77 },
          { date: '2025-04-01', price: 194.35 },
          { date: '2025-04-02', price: 194.65 },
          { date: '2025-04-03', price: 193.9 },
          { date: '2025-04-04', price: 194.08 },
          { date: '2025-04-05', price: 193.45 },
          { date: '2025-04-06', price: 192.86 },
          { date: '2025-04-07', price: 192.54 },
          { date: '2025-04-08', price: 190.08 },
          { date: '2025-04-09', price: 188.73 },
          { date: '2025-04-10', price: 188.56 },
          { date: '2025-04-11', price: 188.1 },
          { date: '2025-04-12', price: 187.92 },
          { date: '2025-04-13', price: 185.05 },
        ],
        upper_bound: [
          { date: '2025-03-15', price: 233.57 },
          { date: '2025-03-16', price: 233.62 },
          { date: '2025-03-17', price: 231.11 },
          { date: '2025-03-18', price: 231.14 },
          { date: '2025-03-19', price: 229.8 },
          { date: '2025-03-20', price: 229.1 },
          { date: '2025-03-21', price: 227.45 },
          { date: '2025-03-22', price: 225.2 },
          { date: '2025-03-23', price: 224.5 },
          { date: '2025-03-24', price: 224.88 },
          { date: '2025-03-25', price: 221.24 },
          { date: '2025-03-26', price: 220.31 },
          { date: '2025-03-27', price: 218.66 },
          { date: '2025-03-28', price: 216.24 },
          { date: '2025-03-29', price: 214.89 },
          { date: '2025-03-30', price: 214.97 },
          { date: '2025-03-31', price: 214.25 },
          { date: '2025-04-01', price: 213.78 },
          { date: '2025-04-02', price: 214.12 },
          { date: '2025-04-03', price: 213.29 },
          { date: '2025-04-04', price: 213.49 },
          { date: '2025-04-05', price: 212.79 },
          { date: '2025-04-06', price: 212.14 },
          { date: '2025-04-07', price: 211.79 },
          { date: '2025-04-08', price: 209.09 },
          { date: '2025-04-09', price: 207.6 },
          { date: '2025-04-10', price: 207.42 },
          { date: '2025-04-11', price: 206.91 },
          { date: '2025-04-12', price: 206.72 },
          { date: '2025-04-13', price: 203.55 },
        ],
        lower_bound: [
          { date: '2025-03-15', price: 191.11 },
          { date: '2025-03-16', price: 191.14 },
          { date: '2025-03-17', price: 189.09 },
          { date: '2025-03-18', price: 189.11 },
          { date: '2025-03-19', price: 188.02 },
          { date: '2025-03-20', price: 187.45 },
          { date: '2025-03-21', price: 186.09 },
          {
            date: '2025-03-22',
            price: 184.26,
          },
          {
            date: '2025-03-23',
            price: 183.68,
          },
          {
            date: '2025-03-24',
            price: 183.99,
          },
          {
            date: '2025-03-25',
            price: 181.02,
          },
          {
            date: '2025-03-26',
            price: 180.25,
          },
          {
            date: '2025-03-27',
            price: 178.9,
          },
          {
            date: '2025-03-28',
            price: 176.92,
          },
          {
            date: '2025-03-29',
            price: 175.82,
          },
          {
            date: '2025-03-30',
            price: 175.88,
          },
          {
            date: '2025-03-31',
            price: 175.29,
          },
          {
            date: '2025-04-01',
            price: 174.91,
          },
          {
            date: '2025-04-02',
            price: 175.19,
          },
          {
            date: '2025-04-03',
            price: 174.51,
          },
          {
            date: '2025-04-04',
            price: 174.67,
          },
          {
            date: '2025-04-05',
            price: 174.1,
          },
          {
            date: '2025-04-06',
            price: 173.57,
          },
          {
            date: '2025-04-07',
            price: 173.28,
          },
          {
            date: '2025-04-08',
            price: 171.07,
          },
          {
            date: '2025-04-09',
            price: 169.85,
          },
          {
            date: '2025-04-10',
            price: 169.71,
          },
          {
            date: '2025-04-11',
            price: 169.29,
          },
          {
            date: '2025-04-12',
            price: 169.13,
          },
          {
            date: '2025-04-13',
            price: 166.54,
          },
        ],
      },
      last_updated: '2025-03-15 00:31:20',
    }
    chartData.value = data.historical_data
    predictionData.value = data.prediction.data
    upperBoundData.value = data.prediction.upper_bound
    lowerBoundData.value = data.prediction.lower_bound

    stockInfo.value = {
      name: data.name,
      sentiment: data.sentiment,
      lastUpdated: data.last_updated,
    }

    emit('chart-loaded', {
      name: data.name,
      ticker: data.ticker,
      historical_data: data.historical_data,
      currentPrice: data.historical_data[data.historical_data.length - 1].price,
      sentiment: data.sentiment,
      last_updated: data.last_updated,
    })
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
