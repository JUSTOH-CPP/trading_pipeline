// chart.js
/**
 * TradingView Lightweight Charts Integration
 * Handles chart rendering, real-time updates, and WebSocket connections
 */

// Global Chart State
let chart = null;
let candleSeries = null;
let buySignalSeries = null;
let sellSignalSeries = null;
let container = null;
let ws = null;
let signalHistory = [];
const MAX_SIGNALS_DISPLAY = 5;

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function () {
    console.log('Dashboard initializing...');

    // Initialize chart
    initializeChart();

    // Fetch initial data
    fetchChartData();
    fetchAccountInfo();

    // Setup periodic updates
    setInterval(fetchAccountInfo, 2000);  // Update account every 2 seconds
    setInterval(fetchOpenPositions, 2000);  // Update positions every 2 seconds
    setInterval(fetchSymbolTick, 1000);  // Update bid/ask every 1 second

    // Connect to WebSocket for real-time updates
    connectWebSocket();
});

// ============================================================================
// CHART INITIALIZATION
// ============================================================================

function initializeChart() {
    container = document.getElementById('chart');

    // Create chart instance
    chart = LightweightCharts.createChart(container, {
        layout: {
            textColor: '#d1d5db',
            background: { type: 'solid', color: '#0f0f1e' }
        },
        width: container.clientWidth,
        height: container.clientHeight,
        timeScale: {
            timeVisible: true,
            secondsVisible: true,
            rightOffset: 12,
            barSpacing: 10
        },
        grid: {
            vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
            hLines: { color: 'rgba(255, 255, 255, 0.05)' }
        }
    });

    // Create candlestick series
    candleSeries = chart.addCandlestickSeries({
        upColor: '#00ff88',
        downColor: '#ff4444',
        borderUpColor: '#00ff88',
        borderDownColor: '#ff4444',
        wickUpColor: '#00ff88',
        wickDownColor: '#ff4444'
    });

    // Create markers series for BUY signals (green triangles)
    buySignalSeries = chart.addMarkerSeries({
        color: '#00ff88',
        autoscaleMarkers: true
    });

    // Create markers series for SELL signals (red triangles)
    sellSignalSeries = chart.addMarkerSeries({
        color: '#ff4444',
        autoscaleMarkers: true
    });

    // Setup responsive resizing
    window.addEventListener('resize', handleChartResize);

    // Add crosshair tooltip
    setupTooltip();

    console.log('Chart initialized successfully');
}

function setupTooltip() {
    const tooltipWidth = 80;
    const tooltipHeight = 80;
    const toolTip = document.createElement('div');
    toolTip.style.width = tooltipWidth + 'px';
    toolTip.style.height = tooltipHeight + 'px';
    toolTip.style.position = 'absolute';
    toolTip.style.display = 'none';
    toolTip.style.padding = '8px';
    toolTip.style.boxSizing = 'border-box';
    toolTip.style.fontSize = '12px';
    toolTip.style.textAlign = 'left';
    toolTip.style.zIndex = '1000';
    toolTip.style.top = '12px';
    toolTip.style.left = '12px';
    toolTip.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    toolTip.style.color = '#00ff88';
    toolTip.style.borderRadius = '4px';
    toolTip.style.border = '1px solid rgba(0, 255, 136, 0.3)';
    toolTip.style.pointerEvents = 'none';
    container.appendChild(toolTip);

    // Update tooltip on mouse movement
    chart.subscribeCrosshairMove((param) => {
        if (!param.point || !param.time) {
            toolTip.style.display = 'none';
            return;
        }

        const data = param.seriesData.get(candleSeries);
        if (!data) {
            return;
        }

        toolTip.style.display = 'block';
        let html = `<div><strong>${formatTime(param.time)}</strong></div>`;
        html += `<div>O: ${data.open.toFixed(5)}</div>`;
        html += `<div>H: ${data.high.toFixed(5)}</div>`;
        html += `<div>L: ${data.low.toFixed(5)}</div>`;
        html += `<div>C: ${data.close.toFixed(5)}</div>`;
        toolTip.innerHTML = html;
    });
}

function handleChartResize() {
    if (chart && container) {
        const width = container.clientWidth;
        const height = container.clientHeight;
        chart.applyOptions({ width, height });
        chart.timeScale().fitContent();
    }
}

// ============================================================================
// DATA FETCHING
// ============================================================================

async function fetchChartData() {
    try {
        document.getElementById('chart-loading').style.display = 'flex';

        const response = await fetch('/api/chart-data');
        const data = await response.json();

        if (data.candles && data.candles.length > 0) {
            // Convert API data to chart format
            const candles = data.candles.map(c => ({
                time: c.time,
                open: c.open,
                high: c.high,
                low: c.low,
                close: c.close
            }));

            // Set candlestick data
            candleSeries.setData(candles);

            // Add signal markers
            if (data.signals && data.signals.length > 0) {
                const buySignals = [];
                const sellSignals = [];

                data.signals.forEach(signal => {
                    const marker = {
                        time: signal.time,
                        position: signal.signal === 1 ? 'belowBar' : 'aboveBar',
                        color: signal.signal === 1 ? '#00ff88' : '#ff4444',
                        shape: signal.signal === 1 ? 'arrowUp' : 'arrowDown',
                        text: signal.signal === 1 ? 'BUY' : 'SELL'
                    };

                    if (signal.signal === 1) {
                        buySignals.push(marker);
                    } else {
                        sellSignals.push(marker);
                    }
                });

                buySignalSeries.setMarkers(buySignals);
                sellSignalSeries.setMarkers(sellSignals);

                // Update signal history
                updateSignalHistory(data.signals);
            }

            // Fit content to view
            chart.timeScale().fitContent();

            // Update symbol display
            document.getElementById('symbol').textContent = data.symbol;

            console.log(`Loaded ${candles.length} candles and ${data.signals.length} signals`);
        }

        document.getElementById('chart-loading').style.display = 'none';
    } catch (error) {
        console.error('Error fetching chart data:', error);
        showNotification('Error loading chart data', 'error');
        document.getElementById('chart-loading').style.display = 'none';
    }
}

async function fetchAccountInfo() {
    try {
        const response = await fetch('/api/account-info');
        const data = await response.json();

        if (data.error) {
            console.warn('Account info error:', data.error);
            return;
        }

        // Update account display
        document.getElementById('balance').textContent = `$${formatNumber(data.balance)}`;
        document.getElementById('equity').textContent = `$${formatNumber(data.equity)}`;

        const profitElement = document.getElementById('profit');
        profitElement.textContent = `$${formatNumber(data.profit)}`;
        profitElement.className = 'stat-value ' + (data.profit >= 0 ? 'positive' : 'negative');

        const marginPercent = data.margin > 0 ? (data.margin / data.equity * 100).toFixed(1) : 0;
        document.getElementById('margin').textContent = `${marginPercent}%`;

    } catch (error) {
        console.error('Error fetching account info:', error);
    }
}

async function fetchOpenPositions() {
    try {
        const response = await fetch('/api/positions');
        const positions = await response.json();

        const container = document.getElementById('positions-container');

        if (!positions || positions.length === 0) {
            container.innerHTML = '<div style="color: #999; font-size: 0.85em; padding: 10px 0;">No open positions</div>';
            return;
        }

        container.innerHTML = '';
        positions.forEach(pos => {
            const profitClass = pos.profit >= 0 ? 'positive' : 'negative';
            const positionClass = pos.type === 'BUY' ? '' : 'sell';

            const posElement = document.createElement('div');
            posElement.className = `position ${positionClass}`;
            posElement.innerHTML = `
                <div class="position-header">
                    <span>${pos.symbol}</span>
                    <span>${pos.type}</span>
                </div>
                <div class="position-detail">
                    <span>Size:</span>
                    <span>${pos.volume.toFixed(2)}</span>
                </div>
                <div class="position-detail">
                    <span>Entry:</span>
                    <span>${pos.open_price.toFixed(5)}</span>
                </div>
                <div class="position-detail">
                    <span>Current:</span>
                    <span>${pos.current_price.toFixed(5)}</span>
                </div>
                <div class="position-detail">
                    <span>P&L:</span>
                    <span class="position-profit ${profitClass}">$${formatNumber(pos.profit)}</span>
                </div>
            `;
            container.appendChild(posElement);
        });

    } catch (error) {
        console.error('Error fetching positions:', error);
    }
}

async function fetchSymbolTick() {
    try {
        const response = await fetch('/api/symbol-tick');
        const data = await response.json();

        if (!data.error) {
            document.getElementById('bid-ask').textContent = 
                `${data.bid.toFixed(5)} / ${data.ask.toFixed(5)}`;
        }
    } catch (error) {
        console.error('Error fetching tick data:', error);
    }
}

// ============================================================================
// WEBSOCKET CONNECTION
// ============================================================================

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/stream`;

    ws = new WebSocket(wsUrl);

    ws.onopen = function () {
        console.log('WebSocket connected');
        updateServerStatus(true);
    };

    ws.onmessage = function (event) {
        try {
            const message = JSON.parse(event.data);

            if (message.type === 'update') {
                // Update chart with new candles
                if (message.candles && message.candles.length > 0) {
                    const lastCandle = message.candles[message.candles.length - 1];
                    candleSeries.update(lastCandle);
                }

                // Update signals
                if (message.signals && message.signals.length > 0) {
                    message.signals.forEach(signal => {
                        const marker = {
                            time: signal.time,
                            position: signal.signal === 1 ? 'belowBar' : 'aboveBar',
                            color: signal.signal === 1 ? '#00ff88' : '#ff4444',
                            shape: signal.signal === 1 ? 'arrowUp' : 'arrowDown',
                            text: signal.signal === 1 ? 'BUY' : 'SELL'
                        };

                        if (signal.signal === 1) {
                            buySignalSeries.update(marker);
                            showNotification(`BUY Signal @ ${signal.price.toFixed(5)}`);
                        } else {
                            sellSignalSeries.update(marker);
                            showNotification(`SELL Signal @ ${signal.price.toFixed(5)}`);
                        }

                        // Add to history
                        signalHistory.unshift({
                            type: signal.signal === 1 ? 'BUY' : 'SELL',
                            price: signal.price,
                            time: new Date(signal.time * 1000).toLocaleTimeString()
                        });

                        // Keep only recent signals
                        if (signalHistory.length > MAX_SIGNALS_DISPLAY) {
                            signalHistory.pop();
                        }

                        updateSignalDisplay();
                    });
                }
            }
        } catch (error) {
            console.error('Error processing WebSocket message:', error);
        }
    };

    ws.onerror = function (error) {
        console.error('WebSocket error:', error);
        updateServerStatus(false);
    };

    ws.onclose = function () {
        console.log('WebSocket disconnected');
        updateServerStatus(false);

        // Attempt to reconnect after 3 seconds
        setTimeout(() => {
            console.log('Attempting to reconnect WebSocket...');
            connectWebSocket();
        }, 3000);
    };
}

// ============================================================================
// UI UPDATES
// ============================================================================

function updateServerStatus(connected) {
    const indicator = document.getElementById('status-indicator');
    const text = document.getElementById('status-text');

    if (connected) {
        indicator.classList.remove('offline');
        text.textContent = 'Live';
    } else {
        indicator.classList.add('offline');
        text.textContent = 'Offline';
    }
}

function updateSignalHistory(signals) {
    signalHistory = [];
    signals.forEach(signal => {
        signalHistory.push({
            type: signal.signal === 1 ? 'BUY' : 'SELL',
            price: signal.price,
            time: new Date(signal.time * 1000).toLocaleTimeString()
        });
    });
    signalHistory = signalHistory.reverse();
    if (signalHistory.length > MAX_SIGNALS_DISPLAY) {
        signalHistory = signalHistory.slice(0, MAX_SIGNALS_DISPLAY);
    }
    updateSignalDisplay();
}

function updateSignalDisplay() {
    const container = document.getElementById('signals-container');

    if (signalHistory.length === 0) {
        container.innerHTML = '<div style="color: #999; font-size: 0.85em; padding: 10px 0;">No signals yet</div>';
        return;
    }

    container.innerHTML = '';
    signalHistory.forEach(signal => {
        const signalColor = signal.type === 'BUY' ? '#00ff88' : '#ff4444';
        const signalElement = document.createElement('div');
        signalElement.style.cssText = `
            padding: 8px;
            margin: 5px 0;
            background: rgba(255, 255, 255, 0.05);
            border-left: 3px solid ${signalColor};
            border-radius: 3px;
            font-size: 0.8em;
            color: #ddd;
        `;
        signalElement.innerHTML = `
            <div style="font-weight: 600; color: ${signalColor};">${signal.type}</div>
            <div style="color: #999; font-size: 0.75em;">${signal.time}</div>
            <div style="color: #bbb;">@ ${signal.price.toFixed(5)}</div>
        `;
        container.appendChild(signalElement);
    });
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function formatNumber(num) {
    return Math.abs(num) >= 1000000 
        ? (num / 1000000).toFixed(2) + 'M'
        : Math.abs(num) >= 1000 
        ? (num / 1000).toFixed(2) + 'K'
        : num.toFixed(2);
}

function formatTime(time) {
    const date = new Date(time * 1000);
    return date.toLocaleString();
}

// ============================================================================
// EXPORT FOR CONSOLE USE
// ============================================================================

window.TradingDashboard = {
    chart,
    candleSeries,
    fetchChartData,
    fetchAccountInfo,
    fetchOpenPositions,
    showNotification
};

console.log('Chart.js loaded. Access dashboard via window.TradingDashboard');
