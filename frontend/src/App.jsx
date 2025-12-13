import { useState } from 'react'
import HeroSelector from './components/HeroSelector'
import BuildRecommendation from './components/BuildRecommendation'
import './App.css'

function App() {
  const [selectedHeroId, setSelectedHeroId] = useState(null)
  const [recommendation, setRecommendation] = useState(null)

  const handleHeroSelect = (heroId) => {
    setSelectedHeroId(heroId)
    setRecommendation(null)
  }

  const handleRecommendation = (data) => {
    setRecommendation(data)
  }

  return (
    <div className="App">
      <header className="header">
        <h1>🔥 Torchlight Infinite Optimizer</h1>
        <p className="subtitle">AI-Powered Build Recommendations</p>
      </header>

      <div className="container">
        <div className="main-content">
          <HeroSelector
            onHeroSelect={handleHeroSelect}
            onRecommendation={handleRecommendation}
            selectedHeroId={selectedHeroId}
          />

          {recommendation && (
            <BuildRecommendation recommendation={recommendation} />
          )}
        </div>
      </div>

      <footer className="footer">
        <p>Powered by Claude Code | Data from tlidb.com</p>
      </footer>
    </div>
  )
}

export default App
