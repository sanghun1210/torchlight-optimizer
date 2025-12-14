import { useState, useEffect } from 'react'
import api from '../services/api'
import './HeroSelector.css'

function HeroSelector({ onHeroSelect, onRecommendation, selectedHeroId, onEngineChange }) {
  const [heroes, setHeroes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [recommending, setRecommending] = useState(false)
  const [useAI, setUseAI] = useState(true) // Default to AI
  const [playstyle, setPlaystyle] = useState('')

  useEffect(() => {
    fetchHeroes()
  }, [])

  const fetchHeroes = async () => {
    try {
      setLoading(true)
      const data = await api.heroes.getAll()
      setHeroes(data)
      setError(null)
    } catch (err) {
      setError('Failed to load heroes: ' + err.message)
      console.error('Error fetching heroes:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleEngineToggle = () => {
    const newUseAI = !useAI
    setUseAI(newUseAI)
    if (onEngineChange) {
      onEngineChange(newUseAI ? 'ai' : 'v2')
    }
  }

  const handleRecommend = async () => {
    if (!selectedHeroId) {
      alert('Please select a hero first!')
      return
    }

    try {
      setRecommending(true)
      let data

      if (useAI) {
        // Use AI recommendation
        data = await api.recommendationsAI.getAIBuildRecommendation(
          selectedHeroId,
          { playstyle: playstyle || undefined }
        )
      } else {
        // Use rule-based v2 recommendation
        data = await api.recommendationsV2.getBuildRecommendation(
          selectedHeroId,
          { playstyle: playstyle || undefined }
        )
      }

      onRecommendation(data)
      setError(null)
    } catch (err) {
      setError(`Failed to get ${useAI ? 'AI' : 'rule-based'} recommendation: ` + err.message)
      console.error('Error getting recommendation:', err)
    } finally {
      setRecommending(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading heroes...</div>
  }

  if (error) {
    return (
      <div className="error">
        {error}
        <button onClick={fetchHeroes} style={{ marginLeft: '1rem' }}>
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="hero-selector">
      <h2>Select Your Hero</h2>

      <div className="hero-grid">
        {heroes.map((hero) => (
          <div
            key={hero.id}
            className={`hero-card ${selectedHeroId === hero.id ? 'selected' : ''}`}
            onClick={() => onHeroSelect(hero.id)}
          >
            {hero.image_url && (
              <img src={hero.image_url} alt={hero.name} className="hero-image" />
            )}
            <div className="hero-info">
              <h3>{hero.name}</h3>
              <p className="hero-talent">{hero.talent}</p>
              <p className="hero-god-type">{hero.god_type}</p>
            </div>
          </div>
        ))}
      </div>

      {selectedHeroId && (
        <div className="recommend-section">
          {/* Engine Toggle */}
          <div className="engine-toggle">
            <label className="toggle-label">
              <input
                type="checkbox"
                checked={useAI}
                onChange={handleEngineToggle}
                className="toggle-input"
              />
              <span className="toggle-slider"></span>
              <span className="toggle-text">
                {useAI ? '🤖 AI-Powered' : '📊 Rule-Based'}
              </span>
            </label>
          </div>

          {/* Playstyle Input */}
          <div className="playstyle-input">
            <label htmlFor="playstyle">
              Playstyle (optional):
            </label>
            <input
              id="playstyle"
              type="text"
              value={playstyle}
              onChange={(e) => setPlaystyle(e.target.value)}
              placeholder="e.g., Melee, DoT, Fire"
              className="playstyle-field"
            />
          </div>

          {/* Recommend Button */}
          <button
            className={`recommend-button ${useAI ? 'ai-mode' : 'v2-mode'}`}
            onClick={handleRecommend}
            disabled={recommending}
          >
            {recommending
              ? (useAI ? '🤖 AI Analyzing...' : '📊 Analyzing...')
              : (useAI ? '🤖 Get AI Recommendation' : '📊 Get Recommendation')
            }
          </button>

          {useAI && (
            <p className="ai-notice">
              💡 AI recommendations may take 5-10 seconds
            </p>
          )}
        </div>
      )}
    </div>
  )
}

export default HeroSelector
