// Stock data by category
const stockData = {
    'US Stocks': [
        { name: 'Apple Inc', symbol: 'AAPL', price: '$185.40', change: '+2.3%', positive: true, shares: '2.9T', icon: '🍎' },
        { name: 'Apple Inc', symbol: 'AAPL', price: '$185.40', change: '+2.3%', positive: true, shares: '2.9T', icon: '🍎' },
        { name: 'Apple Inc', symbol: 'AAPL', price: '$185.40', change: '+2.3%', positive: true, shares: '2.9T', icon: '🍎' },
        { name: 'Apple Inc', symbol: 'AAPL', price: '$185.40', change: '+2.3%', positive: true, shares: '2.9T', icon: '🍎' },
        { name: 'Apple Inc', symbol: 'AAPL', price: '$185.40', change: '+2.3%', positive: true, shares: '2.9T', icon: '🍎' },
        { name: 'Apple Inc', symbol: 'AAPL', price: '$185.40', change: '+2.3%', positive: true, shares: '2.9T', icon: '🍎' }
    ],
    'NG Stocks': [
        { name: 'Dangote Cement', symbol: 'DANGCEM', price: '₦3,850', change: '+1.8%', positive: true, shares: '₦6.5T', icon: '🏭' },
        { name: 'MTN Nigeria', symbol: 'MTNN', price: '₦245', change: '-0.5%', positive: false, shares: '₦5.0T', icon: '📱' },
        { name: 'Guaranty Trust', symbol: 'GTCO', price: '₦28.50', change: '+3.2%', positive: true, shares: '₦800B', icon: '🏦' },
        { name: 'Nestle Nigeria', symbol: 'NESTLE', price: '₦1,450', change: '+2.1%', positive: true, shares: '₦1.2T', icon: '🍫' }
    ],
    'Treasury Bills': [
        { name: '91-Day T-Bill', symbol: '91D', price: '₦98.50', change: '+0.1%', positive: true, shares: 'Gov Backed', icon: '📊' },
        { name: '182-Day T-Bill', symbol: '182D', price: '₦97.20', change: '+0.2%', positive: true, shares: 'Gov Backed', icon: '📈' },
        { name: '364-Day T-Bill', symbol: '364D', price: '₦94.80', change: '+0.3%', positive: true, shares: 'Gov Backed', icon: '📉' }
    ]
};

// Open stock modal
function openStockModal(category) {
    const modal = document.getElementById('stockSelectionModal');
    const title = document.getElementById('stockModalTitle');
    const searchInput = document.getElementById('stockSearchInput');
    
    // Set title
    title.textContent = category;
    
    // Update search placeholder
    searchInput.placeholder = `Search ${category.toLowerCase()}...`;
    searchInput.value = '';
    
    // Load stocks for this category
    loadStocks(category);
    
    // Show modal
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// Close stock modal
function closeStockModal() {
    const modal = document.getElementById('stockSelectionModal');
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

// Load stocks into grid
function loadStocks(category) {
    const grid = document.getElementById('stocksGrid');
    const stocks = stockData[category] || [];
    
    if (stocks.length === 0) {
        grid.innerHTML = `
            <div class="no-results">
                <i class="fas fa-chart-line"></i>
                <p>No stocks available</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = stocks.map(stock => `
        <div class="stock-card" data-stock="${stock.symbol}">
            <div class="stock-header">
                <div class="stock-info-left">
                    <div class="stock-icon">${stock.icon}</div>
                    <div class="stock-name-symbol">
                        <div class="stock-name">${stock.name}</div>
                        <div class="stock-symbol">${stock.symbol}</div>
                    </div>
                </div>
                <div class="stock-change ${stock.positive ? 'positive' : 'negative'}">
                    ${stock.change}
                </div>
            </div>
            
            <div class="stock-chart">
                <div class="chart-bar" style="height: 40%;"></div>
                <div class="chart-bar" style="height: 60%;"></div>
                <div class="chart-bar" style="height: 80%;"></div>
                <div class="chart-bar" style="height: 50%;"></div>
                <div class="chart-bar" style="height: 90%;"></div>
                <div class="chart-bar" style="height: 70%;"></div>
                <div class="chart-bar" style="height: 85%;"></div>
            </div>
            
            <div class="stock-footer">
                <div class="stock-price-info">
                    <div class="stock-price">${stock.price}</div>
                    <div class="stock-shares">${stock.shares}</div>
                </div>
                <button class="buy-btn" onclick="buyStock('${stock.symbol}', '${stock.name}')">
                    Buy
                </button>
            </div>
        </div>
    `).join('');
}

// Filter stocks based on search
function filterStocks() {
    const searchTerm = document.getElementById('stockSearchInput').value.toLowerCase();
    const cards = document.querySelectorAll('.stock-card');
    
    cards.forEach(card => {
        const name = card.querySelector('.stock-name').textContent.toLowerCase();
        const symbol = card.querySelector('.stock-symbol').textContent.toLowerCase();
        
        if (name.includes(searchTerm) || symbol.includes(searchTerm)) {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
}

// Buy stock action
function buyStock(symbol, name) {
    // Close modal
    closeStockModal();
    
    // Show success or open buy confirmation modal
    alert(`Buying ${name} (${symbol})`);
    
    // In production, this would open a buy confirmation modal
    // openBuyConfirmationModal(symbol, name);
}

// Close on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const modal = document.getElementById('stockSelectionModal');
        if (modal && modal.classList.contains('active')) {
            closeStockModal();
        }
    }
});