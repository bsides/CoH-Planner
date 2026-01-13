# Power Enhancement System Implementation Plan

## Goal
Calculate and display three-tier power statistics:
- **Base**: Unenhanced power values from power data
- **Enhanced**: Base + enhancement bonuses from slotted enhancements
- **Final**: Enhanced + set bonuses + active power buff bonuses

## Architecture Components

### 1. Enhancement Value Application (Per-Power)
**File**: `js/enhancement-calculations.js` (new or extend existing)

**Function**: `calculatePowerEnhancementBonuses(power)`
- Input: Power object with slots
- Output: Object with enhancement bonuses per aspect
  ```javascript
  {
    damage: 95.5,      // % bonus from enhancements
    accuracy: 42.4,
    recharge: -35.0,   // negative = faster recharge
    endurance: -50.0,  // negative = reduced cost
    defense: 45.0,
    resistance: 45.0,
    // etc.
  }
  ```

**Logic**:
1. Iterate through power's slots
2. For each slotted enhancement:
   - Get enhancement values (already have this)
   - Apply ED curve to each aspect (already have this)
   - Accumulate bonuses per aspect
3. Return accumulated bonuses

### 2. Power Stat Calculator
**File**: `js/power-stats-calculator.js` (new)

**Function**: `calculatePowerStats(power, options = {})`
- Input: Power object, options for what to include
- Output: Three-tier stat object
  ```javascript
  {
    damage: {
      base: 1.0,
      enhanced: 1.955,    // base * (1 + enhBonus/100)
      final: 2.15         // enhanced * (1 + setBonus/100 + buffBonus/100)
    },
    endurance: {
      base: 0.13,
      enhanced: 0.065,    // base * (1 - enhBonus/100)
      final: 0.0637       // enhanced * (1 - setBonus/100)
    },
    recharge: {
      base: 4.0,
      enhanced: 2.6,      // base / (1 + enhBonus/100)
      final: 2.34         // enhanced / (1 + setBonus/100)
    }
    // ... other aspects
  }
  ```

**Logic**:
1. Get base values from power.effects
2. Calculate enhancement bonuses from slots
3. Get relevant set bonuses from dashboard
4. Get relevant active power buffs
5. Apply bonuses appropriately based on aspect type:
   - **Damage, Accuracy, ToHit**: Multiply (additive bonuses)
   - **Endurance Cost**: Multiply by (1 - reduction%)
   - **Recharge**: Divide by (1 + reduction%)
   - **Defense, Resistance**: Add percentages

### 3. Global Bonus Providers
**Existing**: `stats.js` already has:
- `getAggregatedSetBonuses()` - Returns set bonuses
- `calculateActivePowerBufsBonuses()` - Returns active power buffs

**Enhancement**: Create helper to get bonuses relevant to a specific power:
```javascript
function getRelevantBonusesForPower(power) {
  const setBonuses = getAggregatedSetBonuses();
  const activeBonuses = calculateActivePowerBufsBonuses();

  return {
    damage: (setBonuses.damage || 0) + (activeBonuses.damage || 0),
    accuracy: (setBonuses.accuracy || 0) + (activeBonuses.accuracy || 0),
    recharge: (setBonuses.recharge || 0) + (activeBonuses.recharge || 0),
    endrdx: (setBonuses.endrdx || 0) + (activeBonuses.endrdx || 0),
    // ... etc
  };
}
```

### 4. Tooltip Integration
**File**: `js/tooltips/tooltip-improvements.js`

**Update**: `generateImprovedPowerTooltipHTML()`
- Use `calculatePowerStats()` to get three-tier values
- Display in tooltip format:
  ```
  Damage: 100.0 (195.5) [215.0]
           ^      ^       ^
           base   enhanced final
  ```

### 5. Aspect-Specific Formulas

**Damage/Accuracy/ToHit** (Multiplicative):
```javascript
enhanced = base * (1 + enhBonus / 100)
final = enhanced * (1 + globalBonus / 100)
```

**Endurance Cost** (Reduction):
```javascript
enhanced = base * (1 - enhReduction / 100)
final = enhanced * (1 - globalReduction / 100)
```

**Recharge** (Reduction):
```javascript
enhanced = base / (1 + enhReduction / 100)
final = enhanced / (1 + globalReduction / 100)
```

**Defense/Resistance** (Additive Percentages):
```javascript
enhanced = base + (enhBonus / 100)  // base is already %
final = enhanced + (globalBonus / 100)
```

## Implementation Steps

1. ✅ **Enhancement value extraction** - Already working
2. ✅ **ED curve application** - Already working
3. ✅ **Set bonus tracking** - Already working
4. ✅ **Active power buff tracking** - Already working
5. ⏳ **Power enhancement bonus calculator** - Need to implement
6. ⏳ **Three-tier stat calculator** - Need to implement
7. ⏳ **Tooltip integration** - Need to update
8. ⏳ **Testing with various power types** - Need to verify

## Edge Cases to Handle

- Powers without certain aspects (e.g., toggle with no damage)
- Auto powers vs Toggle vs Click powers
- Powers that provide buffs vs powers that deal damage
- Defense/resistance showing typed values (S/L, E/N, etc.)
- DoT damage calculations
- Heal/Absorb values
- Range, radius, arc values

## Testing Scenarios

1. Attack power with damage enhancements + set bonuses
2. Armor toggle with defense/resistance enhancements
3. Click buff power with recharge enhancements
4. Toggle power showing end cost reduction
5. Power with mixed enhancement types
6. Power with full set slotted (6 pieces + set bonuses)
7. Multiple powers active providing buffs to each other

## Notes

- Keep calculations separate from display logic
- Cache calculations where possible (recalc on slot change)
- Ensure proper rounding for display (2 decimal places)
- Color-code tooltip values (grey=base, white=enhanced, green=final)
- Show formula hints on hover for advanced users
