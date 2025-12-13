import './BuildRecommendation.css'

function BuildRecommendation({ recommendation }) {
  if (!recommendation) return null

  const {
    hero_name,
    hero_talent,
    build_type,
    primary_stat,
    synergy_score,
    build_summary,
    recommended_skills,
    recommended_items,
    recommended_talents,
  } = recommendation

  return (
    <div className="build-recommendation">
      <div className="build-header">
        <h2>{hero_name} - {hero_talent}</h2>
        <div className="build-meta">
          <span className="badge">{build_type} Build</span>
          <span className="badge">{primary_stat}</span>
          <span className="synergy-score">
            Synergy: {synergy_score}/100
          </span>
        </div>
        <p className="build-summary">{build_summary}</p>
      </div>

      <div className="recommendations-grid">
        {/* Recommended Skills */}
        <div className="recommendation-section">
          <h3>🎯 Recommended Skills</h3>
          <div className="items-list">
            {recommended_skills?.map((skill, index) => (
              <div key={index} className="item-card skill-card">
                <div className="item-header">
                  <span className="item-number">#{index + 1}</span>
                  <h4>{skill.skill_name}</h4>
                </div>
                <div className="item-details">
                  <span className="item-type">{skill.skill_type}</span>
                  {skill.damage_type && (
                    <span className="damage-type">{skill.damage_type}</span>
                  )}
                </div>
                <div className="item-tags">
                  {skill.is_dot && <span className="tag dot">DoT</span>}
                  {skill.is_spell_burst_compatible && <span className="tag burst">Spell Burst</span>}
                  {skill.is_combo && <span className="tag combo">Combo</span>}
                </div>
                <p className="item-reason">{skill.reason}</p>
                <div className="item-score">
                  Score: {skill.score.toFixed(1)} | Priority: {skill.priority}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recommended Items */}
        <div className="recommendation-section">
          <h3>⚔️ Recommended Items</h3>
          <div className="items-list">
            {recommended_items?.map((item, index) => (
              <div key={index} className="item-card item-equipment">
                <div className="item-header">
                  <span className="item-number">#{index + 1}</span>
                  <h4>{item.item_name}</h4>
                </div>
                <div className="item-details">
                  <span className="item-slot">{item.slot}</span>
                  {item.rarity && (
                    <span className={`rarity ${item.rarity.toLowerCase()}`}>
                      {item.rarity}
                    </span>
                  )}
                  {item.stat_type && (
                    <span className="stat-type">{item.stat_type}</span>
                  )}
                </div>
                {item.set_name && (
                  <div className="set-name">Set: {item.set_name}</div>
                )}
                <p className="item-reason">{item.reason}</p>
                <div className="item-score">Score: {item.score.toFixed(1)}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Recommended Talents */}
        {recommended_talents && recommended_talents.length > 0 && (
          <div className="recommendation-section full-width">
            <h3>🌟 Recommended Talent Nodes</h3>
            <div className="items-list talents-list">
              {recommended_talents.map((talent, index) => (
                <div key={index} className="item-card talent-card">
                  <div className="item-header">
                    <span className="item-number">#{index + 1}</span>
                    <h4>{talent.node_name}</h4>
                  </div>
                  <div className="item-details">
                    <span className="node-type">{talent.node_type}</span>
                    {talent.tier && <span className="tier">{talent.tier}</span>}
                    {talent.god_class && (
                      <span className="god-class">{talent.god_class}</span>
                    )}
                  </div>
                  <p className="item-reason">{talent.reason}</p>
                  <div className="item-score">Score: {talent.score.toFixed(1)}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default BuildRecommendation
