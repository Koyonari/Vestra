<template>
  <div class="container">
    <h1>Stock Sentiment Analyzer</h1>
    <div class="search-box">
      <input v-model="ticker" placeholder="Enter stock ticker (e.g., AAPL)" />
      <button @click="analyzeSentiment">Analyze</button>
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-if="results.length > 0" class="results">
      <h2>Sentiment Analysis for {{ ticker }}</h2>
      <pie-chart :chart-data="chartData"></pie-chart>

      <h3>News Headlines</h3>
      <div v-for="(article, index) in results" :key="index" class="article">
        <p>{{ article.title }}</p>
        <p class="source">Source: {{ article.source }}</p>
        <p :class="getSentimentClass(article.sentiment)">
          Sentiment: {{ getSentimentLabel(article.sentiment) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import PieChart from '../components/PieChart.vue'

export default {
  components: { PieChart },
  data() {
    return {
      ticker: '',
      results: [],
      loading: false,
      chartData: null,
    }
  },
  methods: {
    async analyzeSentiment() {
      this.loading = true
      try {
        const response = await axios.get(`http://localhost:5000/api/analyze/${this.ticker}`)
        this.results = response.data
        this.prepareChartData()
      } catch (error) {
        console.error('Error fetching data:', error)
      }
      this.loading = false
    },
    getSentimentClass(sentiment) {
      if (sentiment.compound > 0.05) return 'positive'
      if (sentiment.compound < -0.05) return 'negative'
      return 'neutral'
    },
    getSentimentLabel(sentiment) {
      if (sentiment.compound > 0.05) return 'Positive'
      if (sentiment.compound < -0.05) return 'Negative'
      return 'Neutral'
    },
    prepareChartData() {
      // Count positive, negative, neutral articles
      const positive = this.results.filter((a) => a.sentiment.compound > 0.05).length
      const negative = this.results.filter((a) => a.sentiment.compound < -0.05).length
      const neutral = this.results.length - positive - negative

      this.chartData = {
        labels: ['Positive', 'Neutral', 'Negative'],
        datasets: [
          {
            backgroundColor: ['#4CAF50', '#FFC107', '#F44336'],
            data: [positive, neutral, negative],
          },
        ],
      }
    },
  },
}
</script>
