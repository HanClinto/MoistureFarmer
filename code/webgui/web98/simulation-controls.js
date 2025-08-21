// simulation-controls.js - Simulation control functions (pause, delay, scenario management)

/**
 * Set the simulation delay/speed
 */
function setSimulationDelay(simulation_delay) {
    console.log('Setting simulation delay to:', simulation_delay);
    fetch(`/simulation/simulation_delay/${simulation_delay}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then((data) => {
        console.log('Simulation delay set:', data);
    })
    .catch(error => {
        console.error('Error setting simulation delay:', error);
    });

    window.simulationData.simulation_delay = simulation_delay; // Update the local state

    // Update view based on new data
    if (typeof updateSimulationDisplay === 'function') {
        updateSimulationDisplay();
    }
}

/**
 * Toggle the simulation pause state
 */
function toggleSimulationPaused() {
    console.log('Toggling simulation pause');
    fetch(`/simulation/paused/${window.simulationData.paused ? false : true}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log('Simulation paused:', data);
    })
    .catch(error => {
        console.error('Error setting simulation pause:', error);
    });

    window.simulationData.paused = !window.simulationData.paused; // Toggle the local state

    if (typeof updateSimulationDisplay === 'function') {
        updateSimulationDisplay(); // Update the display to reflect the new state
    }
}

/**
 * Create a new scenario on the server by resetting the simulation
 */
function createNewScenario() {
    fetch('/simulation', { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            // Optionally, POST to /scenario/load with a blank scenario structure
            const blankScenario = {
                name: "New Scenario",
                description: "A new scenario.",
                simulation_settings: {},
                entities: []
            };
            fetch('/scenario/load', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(blankScenario)
            })
            .then(resp => resp.json())
            .then(result => {
                if (result.status === 'success') {
                    alert('New scenario created.');
                } else {
                    alert('Error creating scenario: ' + (result.error || 'Unknown error'));
                }
            });
        });
}

/**
 * Open a scenario file from the user's file system
 */
function openScenarioFile() {
    // Create a hidden file input
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json,application/json';
    input.style.display = 'none';
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const scenarioData = JSON.parse(event.target.result);
                fetch('/scenario/load', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(scenarioData)
                })
                .then(resp => resp.json())
                .then(result => {
                    if (result.status === 'success') {
                        alert('Scenario loaded: ' + (scenarioData.name || 'Unnamed'));
                    } else {
                        alert('Error loading scenario: ' + (result.error || 'Unknown error'));
                    }
                });
            } catch (err) {
                alert('Error loading scenario: ' + err);
            }
        };
        reader.readAsText(file);
    };
    document.body.appendChild(input);
    input.click();
    document.body.removeChild(input);
}

/**
 * Save the current scenario to a file
 */
function saveScenarioFile() {
    // Prompt for scenario name/description if desired
    const name = prompt('Enter scenario name:', window.simulationData.name || 'Scenario');
    const description = prompt('Enter scenario description:', window.simulationData.description || '');
    fetch('/scenario/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description })
    })
    .then(response => {
        if (!response.ok) throw new Error('Failed to save scenario');
        return response.blob();
    })
    .then(blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = (name || 'scenario') + '.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    })
    .catch(error => {
        alert('Error saving scenario: ' + error);
    });
}

// Export functions to global scope
window.setSimulationDelay = setSimulationDelay;
window.toggleSimulationPaused = toggleSimulationPaused;
window.createNewScenario = createNewScenario;
window.openScenarioFile = openScenarioFile;
window.saveScenarioFile = saveScenarioFile;
