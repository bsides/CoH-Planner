/**
 * City of Heroes: Rule of 5 System
 * 
 * Tracks set bonuses and enforces the "Rule of 5":
 * Identical set bonus values can only stack 5 times maximum.
 * 
 * Example:
 * - Thunderstrike 4pc gives +9% Accuracy (can stack 5x)
 * - OtherSet 6pc gives +9% Accuracy (counts toward same cap)
 * - DifferentSet 2pc gives +5% Accuracy (separate cap, can stack 5x)
 */

// ============================================
// RULE OF 5 TRACKING
// ============================================

/**
 * Global bonus tracking object
 * Structure:
 * {
 *   'accuracy': {
 *     '9.0': { count: 3, sources: [...], capped: false },
 *     '5.0': { count: 5, sources: [...], capped: true }
 *   },
 *   'damage': { ... }
 * }
 */
const BonusTracking = {};

/**
 * Reset bonus tracking (call when build changes)
 */
function resetBonusTracking() {
    Object.keys(BonusTracking).forEach(key => delete BonusTracking[key]);
}

/**
 * Get all set bonuses from the build with Rule of 5 applied
 * @returns {Object} Aggregated bonuses by stat
 */
function getAggregatedSetBonuses() {
    // Reset tracking
    resetBonusTracking();
    
    // Collect all bonuses from all powers
    const allBonuses = collectAllSetBonuses();
    
    // Track each bonus by stat and value
    allBonuses.forEach(bonus => {
        const stat = bonus.stat;
        const value = parseFloat(bonus.value);
        const valueKey = value.toFixed(2); // Use 2 decimal precision as key
        
        // Initialize stat tracking if needed
        if (!BonusTracking[stat]) {
            BonusTracking[stat] = {};
        }
        
        // Initialize value tracking if needed
        if (!BonusTracking[stat][valueKey]) {
            BonusTracking[stat][valueKey] = {
                count: 0,
                sources: [],
                capped: false,
                value: value
            };
        }
        
        const tracking = BonusTracking[stat][valueKey];
        
        // Only count if under cap
        if (tracking.count < 5) {
            tracking.count++;
            tracking.sources.push(bonus.source);
        } else {
            tracking.capped = true;
        }
    });
    
    // Aggregate totals by stat
    const aggregated = {};
    
    Object.keys(BonusTracking).forEach(stat => {
        let total = 0;
        
        Object.keys(BonusTracking[stat]).forEach(valueKey => {
            const tracking = BonusTracking[stat][valueKey];
            total += tracking.value * tracking.count;
        });
        
        aggregated[stat] = total;
    });
    
    return aggregated;
}

/**
 * Collect all set bonuses from all powers in build
 * @returns {Array} Array of bonus objects
 */
function collectAllSetBonuses() {
    const bonuses = [];
    
    // Helper to process a single power
    const processPower = (power, powerName) => {
        if (!power.slots) return;
        
        // Track which sets are slotted in this power
        const setsInPower = {};
        
        power.slots.forEach(slot => {
            if (slot && slot.type === 'io-set') {
                const setId = slot.setId;
                if (!setsInPower[setId]) {
                    setsInPower[setId] = [];
                }
                setsInPower[setId].push(slot.pieceNum);
            }
        });
        
        // For each set, check how many pieces are slotted
        Object.keys(setsInPower).forEach(setId => {
            const set = IO_SETS[setId];
            if (!set) return;
            
            const pieces = setsInPower[setId];
            const pieceCount = pieces.length;
            
            // Check each set bonus
            set.bonuses.forEach(bonus => {
                // Support two bonus formats: structured objects and legacy strings
                let parsed = null;

                if (typeof bonus === 'string') {
                    // Example string formats: "2 pieces: +3% Damage" or "3 pieces: +9% Accuracy"
                    const m = bonus.match(/(\d+)\s*pieces\s*:\s*\+?([\d.]+)%\s*(.+)/i);
                    if (m) {
                        const pieces = parseInt(m[1], 10);
                        const value = parseFloat(m[2]);
                        const label = m[3].trim();

                        // Map human-readable labels to internal stat keys
                        const labelMap = {
                            'Damage': 'damage',
                            'Accuracy': 'accuracy',
                            'Recharge': 'recharge',
                            'Ranged Defense': 'defRanged',
                            'AoE Defense': 'defAoE',
                            'Melee Defense': 'defMelee',
                            'Max HP': 'maxhp',
                            'Max Endurance': 'maxend',
                            'Recovery': 'recovery',
                            'Regeneration': 'regeneration',
                            'Run Speed': 'runspeed',
                            'Fly Speed': 'flyspeed',
                            'Jump Speed': 'jumpspeed'
                        };

                        // Try direct mapping first, otherwise try to guess by keyword
                        let statKey = labelMap[label] || null;
                        if (!statKey) {
                            if (/damage/i.test(label)) statKey = 'damage';
                            else if (/accuracy/i.test(label)) statKey = 'accuracy';
                            else if (/recharge/i.test(label)) statKey = 'recharge';
                            else if (/ranged defense/i.test(label)) statKey = 'defRanged';
                            else if (/aoe defense/i.test(label)) statKey = 'defAoE';
                            else if (/melee defense/i.test(label)) statKey = 'defMelee';
                            else if (/max hp/i.test(label)) statKey = 'maxhp';
                            else if (/max end/i.test(label)) statKey = 'maxend';
                            else if (/recovery/i.test(label)) statKey = 'recovery';
                            else if (/regeneration/i.test(label)) statKey = 'regeneration';
                            else if (/run speed/i.test(label)) statKey = 'runspeed';
                            else if (/fly speed/i.test(label)) statKey = 'flyspeed';
                            else if (/jump speed/i.test(label)) statKey = 'jumpspeed';
                        }

                        if (statKey) {
                            parsed = {
                                pieces: pieces,
                                stat: statKey,
                                value: value,
                                desc: bonus
                            };
                        }
                    }
                } else if (bonus && typeof bonus === 'object' && bonus.pieces && bonus.stat && (bonus.value !== undefined)) {
                    parsed = bonus;
                }

                if (!parsed) return; // skip unparseable bonus entries (procs, text-only)

                // If stat is missing, try to infer from description
                if (!parsed.stat && parsed.desc) {
                    const desc = parsed.desc;
                    if (/accuracy/i.test(desc)) parsed.stat = 'accuracy';
                    else if (/damage/i.test(desc)) parsed.stat = 'damage';
                    else if (/recharge/i.test(desc)) parsed.stat = 'recharge';
                    else if (/ranged defense/i.test(desc)) parsed.stat = 'defRanged';
                    else if (/aoe defense/i.test(desc)) parsed.stat = 'defAoE';
                    else if (/melee defense/i.test(desc)) parsed.stat = 'defMelee';
                    else if (/max hp/i.test(desc)) parsed.stat = 'maxhp';
                    else if (/max end/i.test(desc)) parsed.stat = 'maxend';
                    else if (/recovery/i.test(desc)) parsed.stat = 'recovery';
                    else if (/regeneration/i.test(desc)) parsed.stat = 'regeneration';
                }

                if (!parsed.stat) {
                    console.warn('Skipping set bonus with unknown stat:', parsed, setId, powerName);
                    return;
                }

                // Only count if we have enough pieces
                if (pieceCount >= parsed.pieces) {
                    bonuses.push({
                        stat: parsed.stat,
                        value: parsed.value,
                        source: `${set.name} (${parsed.pieces}pc in ${powerName})`,
                        setName: set.name,
                        pieceCount: parsed.pieces,
                        powerName: powerName
                    });
                }
            });
        });
    };
    
    // Process primary powers
    if (Build.primary && Build.primary.powers) {
        Build.primary.powers.forEach(power => {
            processPower(power, power.name);
        });
    }
    
    // Process secondary powers
    if (Build.secondary && Build.secondary.powers) {
        Build.secondary.powers.forEach(power => {
            processPower(power, power.name);
        });
    }
    
    // Process pool powers
    if (Build.pools) {
        Build.pools.forEach(pool => {
            if (pool.powers) {
                pool.powers.forEach(power => {
                    processPower(power, power.name);
                });
            }
        });
    }
    
    return bonuses;
}

/**
 * Get detailed breakdown for a specific stat
 * Shows each unique value with count and sources
 * @param {string} stat - Stat name (e.g., 'accuracy', 'damage')
 * @returns {Array} Array of tracking objects
 */
function getStatBreakdown(stat) {
    if (!BonusTracking[stat]) return [];
    
    const breakdown = [];
    
    Object.keys(BonusTracking[stat]).forEach(valueKey => {
        const tracking = BonusTracking[stat][valueKey];
        breakdown.push({
            value: tracking.value,
            count: tracking.count,
            sources: tracking.sources,
            capped: tracking.capped,
            total: tracking.value * tracking.count
        });
    });
    
    // Sort by value descending
    breakdown.sort((a, b) => b.value - a.value);
    
    return breakdown;
}

/**
 * Check if a specific bonus value is at cap for a stat
 * @param {string} stat - Stat name
 * @param {number} value - Bonus value
 * @returns {boolean} True if capped
 */
function isBonusCapped(stat, value) {
    const valueKey = value.toFixed(2);
    return BonusTracking[stat] && 
           BonusTracking[stat][valueKey] && 
           BonusTracking[stat][valueKey].capped;
}

/**
 * Get count of a specific bonus value for a stat
 * @param {string} stat - Stat name
 * @param {number} value - Bonus value
 * @returns {number} Count (0-5)
 */
function getBonusCount(stat, value) {
    const valueKey = value.toFixed(2);
    return BonusTracking[stat] && BonusTracking[stat][valueKey]
        ? BonusTracking[stat][valueKey].count
        : 0;
}

// ============================================
// LEGACY COMPATIBILITY
// ============================================

/**
 * Legacy function - now uses Rule of 5 system
 * @returns {Object} Set bonuses by stat
 */
function calculateSetBonuses() {
    return getAggregatedSetBonuses();
}

/**
 * Legacy function - now uses Rule of 5 system
 * @returns {Array} Active set bonuses
 */
function getActiveSetBonuses() {
    const bonuses = [];
    
    Object.keys(BonusTracking).forEach(stat => {
        Object.keys(BonusTracking[stat]).forEach(valueKey => {
            const tracking = BonusTracking[stat][valueKey];
            
            tracking.sources.forEach(source => {
                bonuses.push({
                    stat: stat,
                    value: tracking.value,
                    source: source,
                    type: 'set'
                });
            });
        });
    });
    
    return bonuses;
}
