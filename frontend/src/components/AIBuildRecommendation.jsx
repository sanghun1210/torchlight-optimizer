import './AIBuildRecommendation.css'

function AIBuildRecommendation({ recommendation }) {
  if (!recommendation) return null

  const {
    hero_name,
    talent_name,
    build_type,
    build_summary,
    recommended_skills = [],
    recommended_items = [],
    synergy_explanation,
    playstyle_tips = [],
    ai_metadata,
    source
  } = recommendation

  return (
    <div className="ai-build-recommendation">
      {/* Header */}
      <div className="ai-build-header">
        <div className="ai-badge">
          <span className="ai-icon">🤖</span>
          <span>AI-Powered Recommendation</span>
        </div>
        <h2>{hero_name} - {talent_name}</h2>
        <div className="build-meta">
          <span className="badge build-type">{build_type}</span>
          {ai_metadata && (
            <span className="badge tokens">
              {ai_metadata.tokens_used} tokens used
            </span>
          )}
        </div>
        <p className="build-summary">{build_summary}</p>
      </div>

      {/* Synergy Explanation */}
      {synergy_explanation && (
        <div className="synergy-section">
          <h3>⚡ Synergy Analysis</h3>
          <div className="synergy-content">
            <p>{synergy_explanation}</p>
          </div>
        </div>
      )}

      <div className="recommendations-grid">
        {/* Recommended Skills */}
        {recommended_skills.length > 0 && (
          <div className="recommendation-section">
            <h3>🎯 Recommended Skills</h3>
            <div className="items-list">
              {recommended_skills.map((skill, index) => (
                <div key={index} className="ai-item-card skill-card">
                  <div className="item-header">
                    <span className="item-number">#{index + 1}</span>
                    <h4>{skill.skill_name}</h4>
                  </div>
                  {skill.priority && (
                    <div className="priority-badge">
                      Priority: {skill.priority}
                    </div>
                  )}
                  <p className="item-reason">
                    <strong>Why:</strong> {skill.reason}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommended Items */}
        {recommended_items.length > 0 && (
          <div className="recommendation-section">
            <h3>⚔️ Recommended Items</h3>
            <div className="items-list">
              {recommended_items.map((item, index) => (
                <div key={index} className="ai-item-card item-equipment">
                  <div className="item-header">
                    <span className="item-number">#{index + 1}</span>
                    <h4>{item.item_name}</h4>
                  </div>
                  {item.slot && (
                    <div className="item-details">
                      <span className="item-slot">{item.slot}</span>
                    </div>
                  )}
                  <p className="item-reason">
                    <strong>Why:</strong> {item.reason}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Playstyle Tips */}
      {playstyle_tips && playstyle_tips.length > 0 && (
        <div className="tips-section">
          <h3>💡 Playstyle Tips</h3>
          <ul className="tips-list">
            {playstyle_tips.map((tip, index) => (
              <li key={index} className="tip-item">
                {tip}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* AI Metadata */}
      {ai_metadata && (
        <div className="ai-metadata">
          <small>
            Model: {ai_metadata.model || 'gpt-4o-mini'} |
            Tokens: {ai_metadata.tokens_used} ({ai_metadata.prompt_tokens} prompt + {ai_metadata.completion_tokens} completion)
          </small>
        </div>
      )}
    </div>
  )
}

export default AIBuildRecommendation
