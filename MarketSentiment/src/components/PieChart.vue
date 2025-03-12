<!-- // src/components/PieChart.vue 
import { Pie } from 'vue-chartjs' 
import { Chart as ChartJS,
ArcElement, Tooltip, Legend, Title } from 'chart.js' ChartJS.register(ArcElement, Tooltip, Legend,
Title) export default { name: 'PieChart', components: { Pie }, props: { chartData: { type: Object,
required: true }, chartOptions: { type: Object, default: () => ({ responsive: true,
maintainAspectRatio: false, plugins: { legend: { position: 'top', }, title: { display: true, text:
'Sentiment Analysis Distribution', font: { size: 16 } }, tooltip: { callbacks: { label:
function(context) { const label = context.label || ''; const value = context.formattedValue; const
total = context.dataset.data.reduce((a, b) => a + b, 0); const percentage = Math.round((context.raw
/ total) * 100); return `${label}: ${value} (${percentage}%)`; } } } } }) } }, render() { return (
<div style="position: relative; height: 300px">
        <Pie
          data={this.chartData}
          options={this.chartOptions}
        />
      </div>
) } } -->

<template>
  <div class="container">
    <h1>PieChart</h1>
    <div class="search-box"></div>
  </div>
</template>
