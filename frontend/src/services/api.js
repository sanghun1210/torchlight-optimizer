/**
 * API Service - Centralized API calls
 */
import axios from 'axios'

const API_BASE_URL = '/api'

/**
 * Heroes API
 */
export const heroesAPI = {
  /**
   * Get all heroes
   */
  getAll: async () => {
    const response = await axios.get(`${API_BASE_URL}/heroes`)
    return response.data
  },

  /**
   * Get hero by ID
   */
  getById: async (heroId) => {
    const response = await axios.get(`${API_BASE_URL}/heroes/${heroId}`)
    return response.data
  }
}

/**
 * Recommendations API - Rule-based (v2 engine)
 */
export const recommendationsV2API = {
  /**
   * Get build recommendation using rule-based engine
   */
  getBuildRecommendation: async (heroId, params = {}) => {
    const { playstyle, focus, maxSkills = 6, maxItems = 10 } = params
    const queryParams = new URLSearchParams({
      ...(playstyle && { playstyle }),
      ...(focus && { focus }),
      max_skills: maxSkills,
      max_items: maxItems
    })

    const response = await axios.get(
      `${API_BASE_URL}/recommendations/build/${heroId}?${queryParams}`
    )
    return response.data
  },

  /**
   * Get quick recommendation
   */
  getQuickRecommendation: async (heroId) => {
    const response = await axios.get(
      `${API_BASE_URL}/recommendations/quick/${heroId}`
    )
    return response.data
  }
}

/**
 * Recommendations API - AI-powered
 */
export const recommendationsAIAPI = {
  /**
   * Get AI-powered build recommendation
   */
  getAIBuildRecommendation: async (heroId, params = {}) => {
    const { playstyle, maxSkills = 6, maxItems = 10 } = params
    const queryParams = new URLSearchParams({
      ...(playstyle && { playstyle }),
      max_skills: maxSkills,
      max_items: maxItems
    })

    const response = await axios.get(
      `${API_BASE_URL}/recommendations/ai/build/${heroId}?${queryParams}`
    )
    return response.data
  },

  /**
   * Get quick AI recommendation
   */
  getQuickAIRecommendation: async (heroId) => {
    const response = await axios.get(
      `${API_BASE_URL}/recommendations/ai/quick/${heroId}`
    )
    return response.data
  }
}

/**
 * Skills API
 */
export const skillsAPI = {
  getAll: async () => {
    const response = await axios.get(`${API_BASE_URL}/skills`)
    return response.data
  }
}

/**
 * Items API
 */
export const itemsAPI = {
  getAll: async () => {
    const response = await axios.get(`${API_BASE_URL}/items`)
    return response.data
  }
}

export default {
  heroes: heroesAPI,
  recommendationsV2: recommendationsV2API,
  recommendationsAI: recommendationsAIAPI,
  skills: skillsAPI,
  items: itemsAPI
}
