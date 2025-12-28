/**
 * Debug Functions
 * Quick setup functions for testing
 */

/**
 * Debug button: Instantly set up Fire/Fire Blaster
 */
function debugFireFire() {
    console.log('🔥 Debug: Setting up Fire/Fire Blaster');
    
    // 1. Set Archetype
    const archetypeSelect = document.getElementById('archetypeSelect');
    archetypeSelect.value = 'blaster';
    onArchetypeChange();
    
    // 2. Set Primary (Fire Blast)
    setTimeout(() => {
        const primarySelect = document.getElementById('primarySelect');
        primarySelect.value = 'fire-blast';
        onPrimaryChange();
        
        // 3. Set Secondary (Fire Manipulation)
        setTimeout(() => {
            const secondarySelect = document.getElementById('secondarySelect');
            secondarySelect.value = 'fire-manipulation';
            onSecondaryChange();
            
            console.log('✓ Fire/Fire Blaster ready for testing!');
        }, 100);
    }, 100);
}

// Add Fire Blast and Fire Manipulation to POWERSETS if they're loaded
if (typeof FIRE_BLAST_POWERSET !== 'undefined') {
    POWERSETS['fire-blast'] = FIRE_BLAST_POWERSET;
    console.log('✓ Loaded Fire Blast powerset');
}

if (typeof FIRE_MANIPULATION_POWERSET !== 'undefined') {
    POWERSETS['fire-manipulation'] = FIRE_MANIPULATION_POWERSET;
    console.log('✓ Loaded Fire Manipulation powerset');
}
