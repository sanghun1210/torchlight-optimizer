import { useState, useEffect } from 'react'
import axios from 'axios'
import './HeroSelector.css'

function HeroSelector({ onHeroSelect, onRecommendation, selectedHeroId }) {
  const [heroes, setHeroes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [recommending, setRecommending] = useState(false)

  useEffect(() => {
    fetchHeroes()
  }, [])

  const fetchHeroes = async () => {
    try {
      setLoading(true)
      const response = await axios.get('/api/heroes')
      setHeroes(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to load heroes: ' + err.message)
      console.error('Error fetching heroes:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleRecommend = async () => {
    if (!selectedHeroId) {
      alert('Please select a hero first!')
      return
    }

    try {
      setRecommending(true)
      const response = await axios.get(`/api/recommend/build/${selectedHeroId}`)
      onRecommendation(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to get recommendation: ' + err.message)
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
          <button
            className="recommend-button"
            onClick={handleRecommend}
            disabled={recommending}
          >
            {recommending ? 'Analyzing...' : 'Get Build Recommendation'}
          </button>
        </div>
      )}
    </div>
  )
}

export default HeroSelector
