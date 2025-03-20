// First create a type file for better type safety
export interface SentimentItem {
  ticker: string
  name: string
  avg_sentiment: number
  sentiment_category: string
  investment_score: number
  news_count: number
  rank: number
}
