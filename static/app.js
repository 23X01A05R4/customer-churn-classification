document.addEventListener('DOMContentLoaded', () => {
    // 1. Sync Slider Controls Displays
    const tenureInput = document.getElementById('tenure');
    const tenureVal = document.getElementById('tenure-val');
    const monthlyInput = document.getElementById('MonthlyCharges');
    const monthlyVal = document.getElementById('monthly-charges-val');

    if (tenureInput && tenureVal) {
        tenureInput.addEventListener('input', (e) => {
            tenureVal.textContent = `${e.target.value} month${e.target.value > 1 ? 's' : ''}`;
        });
    }

    if (monthlyInput && monthlyVal) {
        monthlyInput.addEventListener('input', (e) => {
            monthlyVal.textContent = `$${parseFloat(e.target.value).toFixed(2)}`;
        });
    }

    // 2. Collapsible Advanced Fields Logic
    const advancedToggleBtn = document.getElementById('advanced-toggle-btn');
    const advancedFields = document.getElementById('advanced-fields');

    if (advancedToggleBtn && advancedFields) {
        advancedToggleBtn.addEventListener('click', () => {
            const isCollapsed = advancedFields.classList.contains('collapsed');
            
            if (isCollapsed) {
                advancedFields.classList.remove('collapsed');
                advancedToggleBtn.setAttribute('aria-expanded', 'true');
                advancedFields.setAttribute('aria-hidden', 'false');
                advancedToggleBtn.textContent = '⚙️ Advanced Customer Profile (Click to collapse)';
            } else {
                advancedFields.classList.add('collapsed');
                advancedToggleBtn.setAttribute('aria-expanded', 'false');
                advancedFields.setAttribute('aria-hidden', 'true');
                advancedToggleBtn.textContent = '⚙️ Advanced Customer Profile (Click to expand)';
            }
        });
    }

    // 3. Tab Navigation Controls in Performance Card
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');

            // Set buttons active state
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Toggle tab content display
            tabContents.forEach(content => {
                if (content.id === `tab-${targetTab}`) {
                    content.classList.add('active');
                } else {
                    content.classList.remove('active');
                }
            });
        });
    });

    // 4. Handle Churn Prediction Form Submission
    const churnForm = document.getElementById('churn-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn ? submitBtn.querySelector('.btn-text') : null;
    const loader = submitBtn ? submitBtn.querySelector('.loader') : null;

    const placeholderCard = document.getElementById('results-placeholder');
    const activeResultsCard = document.getElementById('results-active');
    
    const predictionBadge = document.getElementById('prediction-badge');
    const riskLevelBadge = document.getElementById('risk-level-badge');
    const churnProbabilityText = document.getElementById('churn-probability');
    const predictionMessageText = document.getElementById('prediction-message');
    const gaugeProgress = document.querySelector('.gauge-progress');
    const resultsContainer = document.getElementById('prediction-results');

    if (churnForm) {
        churnForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Set loading state on button
            if (submitBtn) submitBtn.disabled = true;
            if (btnText) btnText.textContent = 'Processing Prediction...';
            if (loader) loader.classList.remove('hidden');

            // Gather values from form
            const formData = new FormData(churnForm);
            const payload = {};
            formData.forEach((value, key) => {
                payload[key] = value;
            });

            // Post values to Flask backend api
            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload),
                });

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.error || 'Server error encountered during prediction.');
                }

                // Hide placeholder card, display prediction results card
                if (placeholderCard) placeholderCard.classList.add('hidden');
                if (activeResultsCard) activeResultsCard.classList.remove('hidden');

                // Render metrics to output elements
                const isChurn = result.churn === 1;
                const probability = result.probability;
                const riskLevel = result.risk_level;

                // Adjust elements classes based on risk status
                if (resultsContainer) {
                    resultsContainer.classList.remove('churn-safe', 'churn-risk');
                    resultsContainer.classList.add(isChurn ? 'churn-risk' : 'churn-safe');
                }

                if (predictionBadge) {
                    predictionBadge.textContent = isChurn ? 'HIGH RISK' : 'SAFE';
                }

                if (riskLevelBadge) {
                    riskLevelBadge.textContent = riskLevel;
                    // Apply subclass colors on secondary badge
                    riskLevelBadge.className = 'risk-badge';
                    if (riskLevel === 'Critical' || riskLevel === 'High') {
                        riskLevelBadge.classList.add('churn-risk-high');
                    } else if (riskLevel === 'Medium') {
                        riskLevelBadge.classList.add('churn-risk-med');
                    }
                }

                if (churnProbabilityText) {
                    churnProbabilityText.textContent = `${(probability * 100).toFixed(1)}%`;
                }

                // Animate Conic-Gradient Circular Gauge based on prediction risk
                if (gaugeProgress) {
                    const degrees = probability * 360;
                    const colorVar = isChurn ? 'var(--color-crimson)' : 'var(--color-indigo)';
                    gaugeProgress.style.backgroundImage = `conic-gradient(${colorVar} ${degrees}deg, var(--bg-dark) 0deg)`;
                }

                // Custom message display
                if (predictionMessageText) {
                    const tenure = result.metrics.tenure;
                    const contract = result.metrics.Contract;
                    
                    if (isChurn) {
                        predictionMessageText.innerHTML = `⚠️ This customer is <strong>highly likely to leave</strong> the service.<br><span style="font-size: 0.85em; color: var(--text-secondary)">Churn driver: Month-to-month contracts or high monthly charges.</span>`;
                    } else {
                        predictionMessageText.innerHTML = `✅ This customer is <strong>likely to remain loyal</strong>.<br><span style="font-size: 0.85em; color: var(--text-secondary)">Retention indicators: Stable contract and tenure of ${tenure} months.</span>`;
                    }
                }

            } catch (err) {
                console.error(err);
                alert(`Error: ${err.message}`);
            } finally {
                // Reset loading state on button
                if (submitBtn) submitBtn.disabled = false;
                if (btnText) btnText.textContent = 'Analyze Customer Profile';
                if (loader) loader.classList.add('hidden');
            }
        });
    }
});
