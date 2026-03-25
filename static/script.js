let currentRole = null;

document.addEventListener("DOMContentLoaded", () => {
    // UI Elements
    const loginScreen = document.getElementById("login-screen");
    const dashboardScreen = document.getElementById("dashboard-screen");
    const navLogout = document.getElementById("nav-logout");
    const activeUserRole = document.getElementById("active-user-role");
    const roleLabel = document.getElementById("role-label");
    const dashTitle = document.getElementById("dash-title");
    const dashSubtitle = document.getElementById("dash-subtitle");
    const farmerSummaryArea = document.getElementById("farmer-summary-area");
    const marketSummaryContent = document.getElementById("market-summary-content");

    const fetchBtn = document.getElementById("fetch-btn");
    const resultsArea = document.getElementById("results-area");
    const loadingState = document.getElementById("loading");
    const contentState = document.getElementById("content");
    const errorState = document.getElementById("error-box");

    const insightTitle = document.getElementById("insight-title");
    const targetDateEl = document.getElementById("target-date");
    const estPriceEl = document.getElementById("est-price");
    const insightMsgEl = document.getElementById("insight-msg");
    const chartFrameEl = document.getElementById("chart-frame");

    // Login Logic
    document.querySelectorAll(".role-card").forEach(card => {
        card.addEventListener("click", () => {
            currentRole = card.getAttribute("data-role");
            initDashboard();
        });
    });

    // Logout Logic
    navLogout.addEventListener("click", (e) => {
        e.preventDefault();
        currentRole = null;

        // Reset UI
        dashboardScreen.classList.add("hidden");
        navLogout.classList.add("hidden");
        activeUserRole.classList.add("hidden");
        resultsArea.classList.add("hidden");
        farmerSummaryArea.classList.add("hidden");

        loginScreen.classList.remove("hidden");
    });

    // Initialize Dashboard based on role
    async function initDashboard() {
        loginScreen.classList.add("hidden");
        dashboardScreen.classList.remove("hidden");
        navLogout.classList.remove("hidden");
        activeUserRole.classList.remove("hidden");

        const displayRole = currentRole.charAt(0).toUpperCase() + currentRole.slice(1);
        roleLabel.textContent = displayRole;

        if (currentRole === 'farmer') {
            dashTitle.textContent = "Maximize Your Harvest Profit";
            dashSubtitle.textContent = "AI-driven price forecasting to find the absolute best day to sell.";
            insightTitle.textContent = "Optimal Sell Window";

            // Fetch live market summary
            farmerSummaryArea.classList.remove("hidden");
            try {
                const res = await fetch('/market_summary');
                const data = await res.json();
                marketSummaryContent.innerHTML = `
                    <div class="summary-metrics">
                        <div>Cardamom: <span class="highlight">Rs ${data.cardamom_current_price}/kg</span></div>
                        <div>Pepper: <span class="highlight">Rs ${data.pepper_current_price}/kg</span></div>
                    </div>
                    <p class="summary-verdict">${data.message}</p>
                `;
            } catch (e) {
                marketSummaryContent.textContent = "Unable to load market summary.";
            }

        } else {
            dashTitle.textContent = "Strategic Bulk Buying";
            dashSubtitle.textContent = "AI-driven forecasting to identify market dips and lowest price points.";
            insightTitle.textContent = "Optimal Buy Window";
            farmerSummaryArea.classList.add("hidden");
        }
    }

    // Fetch Forecast Logic
    fetchBtn.addEventListener("click", async () => {
        const commodity = document.querySelector('input[name="commodity"]:checked').value;

        resultsArea.classList.remove("hidden");
        loadingState.classList.remove("hidden");
        contentState.classList.add("hidden");
        errorState.classList.add("hidden");

        resultsArea.scrollIntoView({ behavior: 'smooth', block: 'start' });

        try {
            // Include role in API request
            const response = await fetch(`/forecast?commodity=${commodity}&role=${currentRole}`);
            if (!response.ok) throw new Error("API Network error");

            const data = await response.json();
            const insight = data.insight;

            const d = new Date(insight.recommended_date || insight.recommended_buy_date);
            const formattedDate = d.toLocaleDateString('en-US', { day: 'numeric', month: 'long', year: 'numeric' });

            targetDateEl.textContent = formattedDate;
            estPriceEl.textContent = insight.expected_price_rs_kg;
            insightMsgEl.textContent = insight.message;

            chartFrameEl.src = `${data.chart_url}?t=${new Date().getTime()}`;

            setTimeout(() => {
                loadingState.classList.add("hidden");
                contentState.classList.remove("hidden");
            }, 500);

        } catch (error) {
            console.error("Forecast Error:", error);
            loadingState.classList.add("hidden");
            errorState.classList.remove("hidden");
        }
    });
});
