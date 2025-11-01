// Global Variables
let allTransactions = [];
let allBudgets = [];
let currentCurrency = '₹';
let categoryChart = null;
let incomeExpenseChart = null;
let monthlyChart = null;
let currentFilter = 'all';

// Categories
const incomeCategories = ['Salary', 'Freelance', 'Investment', 'Gifts', 'Other Income'];
const expenseCategories = ['Food', 'Transport', 'Entertainment', 'Shopping', 'Bills & Utilities', 'Education', 'Healthcare', 'Other Expense'];

// Initialize App
document.addEventListener('DOMContentLoaded', function() {
    loadData();
    setDefaultDate();
    updateCategories();
    populateBudgetCategories();
    updateDashboard();
    setupCharts();
    
    // Set current month for budget
    const today = new Date();
    document.getElementById('budgetMonth').valueAsDate = today;
});

// Data Management
function saveData() {
    localStorage.setItem('transactions', JSON.stringify(allTransactions));
    localStorage.setItem('budgets', JSON.stringify(allBudgets));
}

function loadData() {
    const transactions = localStorage.getItem('transactions');
    const budgets = localStorage.getItem('budgets');
    
    if (transactions) allTransactions = JSON.parse(transactions);
    if (budgets) allBudgets = JSON.parse(budgets);
}

function setDefaultDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('transactionDate').value = today;
}

// Tab Navigation
function switchTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.style.display = 'none');
    
    // Show selected tab
    document.getElementById(tabName).style.display = 'block';
    
    // Update nav links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => link.classList.remove('active'));
    event.target.classList.add('active');
    
    // Refresh charts when switching tabs
    if (tabName === 'analytics') {
        setTimeout(() => {
            if (incomeExpenseChart) incomeExpenseChart.resize();
            if (monthlyChart) monthlyChart.resize();
            if (categoryChart) categoryChart.resize();
        }, 100);
    }
}

// Categories Update
function updateCategories() {
    const type = document.getElementById('transactionType').value;
    const categories = type === 'income' ? incomeCategories : expenseCategories;
    const select = document.getElementById('transactionCategory');
    
    select.innerHTML = '<option value="">Select category</option>';
    categories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        select.appendChild(option);
    });
}

function populateBudgetCategories() {
    const select = document.getElementById('budgetCategory');
    select.innerHTML = '<option value="">Select category</option>';
    expenseCategories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        select.appendChild(option);
    });
}

// Add Transaction
function addTransaction() {
    const amount = parseFloat(document.getElementById('transactionAmount').value);
    const type = document.getElementById('transactionType').value;
    const category = document.getElementById('transactionCategory').value;
    const description = document.getElementById('transactionDescription').value;
    const date = document.getElementById('transactionDate').value;
    
    if (!amount || !category || !date) {
        alert('Please fill all required fields');
        return;
    }
    
    const transaction = {
        id: Date.now(),
        amount,
        type,
        category,
        description,
        date,
        timestamp: new Date().toISOString()
    };
    
    allTransactions.push(transaction);
    saveData();
    updateDashboard();
    updateAnalytics();
    
    // Reset form and close modal
    document.getElementById('addTransactionForm').reset();
    setDefaultDate();
    bootstrap.Modal.getInstance(document.getElementById('addTransactionModal')).hide();
    
    showSuccessMessage('Transaction added successfully!');
}

// Add Budget
function addBudget() {
    const category = document.getElementById('budgetCategory').value;
    const amount = parseFloat(document.getElementById('budgetAmount').value);
    const month = document.getElementById('budgetMonth').value;
    
    if (!category || !amount || !month) {
        alert('Please fill all required fields');
        return;
    }
    
    const existingBudget = allBudgets.find(b => b.category === category && b.month === month);
    if (existingBudget) {
        existingBudget.amount = amount;
    } else {
        allBudgets.push({ id: Date.now(), category, amount, month });
    }
    
    saveData();
    updateBudgets();
    document.getElementById('addBudgetForm').reset();
    bootstrap.Modal.getInstance(document.getElementById('addBudgetModal')).hide();
    
    showSuccessMessage('Budget added successfully!');
}

// Delete Transaction
function deleteTransaction(id) {
    if (confirm('Are you sure you want to delete this transaction?')) {
        allTransactions = allTransactions.filter(t => t.id !== id);
        saveData();
        updateDashboard();
        updateAnalytics();
        showSuccessMessage('Transaction deleted!');
    }
}

// Delete Budget
function deleteBudget(id) {
    if (confirm('Are you sure you want to delete this budget?')) {
        allBudgets = allBudgets.filter(b => b.id !== id);
        saveData();
        updateBudgets();
        showSuccessMessage('Budget deleted!');
    }
}

// Update Dashboard
function updateDashboard() {
    const totalIncome = allTransactions
        .filter(t => t.type === 'income')
        .reduce((sum, t) => sum + t.amount, 0);
    
    const totalExpenses = allTransactions
        .filter(t => t.type === 'expense')
        .reduce((sum, t) => sum + t.amount, 0);
    
    const balance = totalIncome - totalExpenses;
    
    document.getElementById('totalBalance').textContent = formatCurrency(balance);
    document.getElementById('totalIncome').textContent = formatCurrency(totalIncome);
    document.getElementById('totalExpenses').textContent = formatCurrency(totalExpenses);
    
    displayRecentTransactions();
    updateCategoryChart();
}

function displayRecentTransactions() {
    const recent = allTransactions.slice(-5).reverse();
    const container = document.getElementById('recentTransactions');
    
    if (recent.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="bi bi-inbox"></i><p>No transactions yet</p></div>';
        return;
    }
    
    container.innerHTML = recent.map(t => `
        <div class="transaction-row">
            <div class="transaction-info">
                <div class="transaction-category">${t.category}</div>
                <div class="transaction-date">${formatDate(t.date)}</div>
            </div>
            <div class="transaction-amount ${t.type === 'income' ? 'amount-income' : 'amount-expense'}">
                ${t.type === 'income' ? '+' : '-'}${formatCurrency(t.amount)}
            </div>
        </div>
    `).join('');
}

// Filter Transactions
function filterTransactions(type) {
    currentFilter = type;
    
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    displayTransactionsList();
}

function displayTransactionsList() {
    let filtered = allTransactions;
    
    if (currentFilter === 'income') {
        filtered = filtered.filter(t => t.type === 'income');
    } else if (currentFilter === 'expense') {
        filtered = filtered.filter(t => t.type === 'expense');
    }
    
    filtered.sort((a, b) => new Date(b.date) - new Date(a.date));
    
    const container = document.getElementById('transactionsList');
    
    if (filtered.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="bi bi-inbox"></i><p>No transactions found</p></div>';
        return;
    }
    
    container.innerHTML = filtered.map(t => `
        <div class="transaction-row">
            <div class="transaction-info">
                <div class="transaction-category">
                    <span class="badge ${t.type === 'income' ? 'badge-income' : 'badge-expense'}">
                        ${t.type === 'income' ? 'Income' : 'Expense'}
                    </span>
                    ${t.category}
                </div>
                <div class="transaction-date">${formatDate(t.date)} - ${t.description || 'No description'}</div>
            </div>
            <div style="display: flex; gap: 10px;">
                <div class="transaction-amount ${t.type === 'income' ? 'amount-income' : 'amount-expense'}">
                    ${t.type === 'income' ? '+' : '-'}${formatCurrency(t.amount)}
                </div>
                <button class="btn btn-sm btn-danger" onclick="deleteTransaction(${t.id})">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// Update Budgets
function updateBudgets() {
    const currentMonth = new Date().toISOString().substring(0, 7);
    const currentBudgets = allBudgets.filter(b => b.month === currentMonth);
    
    const container = document.getElementById('budgetsList');
    
    if (currentBudgets.length === 0) {
        container.innerHTML = '<p class="text-muted">No budgets set for this month</p>';
        return;
    }
    
    container.innerHTML = currentBudgets.map(budget => {
        const spent = allTransactions
            .filter(t => t.type === 'expense' && t.category === budget.category && t.date.substring(0, 7) === currentMonth)
            .reduce((sum, t) => sum + t.amount, 0);
        
        const percentage = (spent / budget.amount) * 100;
        const isWarning = percentage >= 80;
        
        return `
            <div class="mb-3">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span class="fw-bold">${budget.category}</span>
                    <span>${formatCurrency(spent)} / ${formatCurrency(budget.amount)}</span>
                </div>
                <div class="budget-progress">
                    <div class="budget-progress-bar ${isWarning ? 'warning' : ''}" style="width: ${Math.min(percentage, 100)}%">
                        ${Math.round(percentage)}%
                    </div>
                </div>
                <button class="btn btn-sm btn-danger mt-2" onclick="deleteBudget(${budget.id})">
                    <i class="bi bi-trash"></i> Delete
                </button>
            </div>
        `;
    }).join('');
}

// Analytics
function updateAnalytics() {
    const currentMonth = new Date().toISOString().substring(0, 7);
    
    // Category breakdown
    const categoryBreakdown = {};
    allTransactions
        .filter(t => t.type === 'expense' && t.date.substring(0, 7) === currentMonth)
        .forEach(t => {
            categoryBreakdown[t.category] = (categoryBreakdown[t.category] || 0) + t.amount;
        });
    
    const breakdownContainer = document.getElementById('categoryBreakdown');
    if (Object.keys(categoryBreakdown).length === 0) {
        breakdownContainer.innerHTML = '<p class="text-muted">No expenses this month</p>';
    } else {
        breakdownContainer.innerHTML = Object.entries(categoryBreakdown)
            .sort((a, b) => b[1] - a[1])
            .map(([cat, amount]) => `
                <div class="mb-2" style="display: flex; justify-content: space-between; align-items: center;">
                    <span>${cat}</span>
                    <strong>${formatCurrency(amount)}</strong>
                </div>
            `).join('');
    }
}

// Chart Setup
function setupCharts() {
    updateCategoryChart();
    updateIncomeExpenseChart();
    updateMonthlyChart();
}

function updateCategoryChart() {
    const currentMonth = new Date().toISOString().substring(0, 7);
    const categoryData = {};
    
    allTransactions
        .filter(t => t.type === 'expense' && t.date.substring(0, 7) === currentMonth)
        .forEach(t => {
            categoryData[t.category] = (categoryData[t.category] || 0) + t.amount;
        });
    
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;
    
    if (categoryChart) categoryChart.destroy();
    
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(categoryData),
            datasets: [{
                data: Object.values(categoryData),
                backgroundColor: [
                    '#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe',
                    '#43e97b', '#fa709a', '#fee140', '#30cfd0', '#330867'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

function updateIncomeExpenseChart() {
    const months = {};
    
    allTransactions.forEach(t => {
        const month = t.date.substring(0, 7);
        if (!months[month]) months[month] = { income: 0, expense: 0 };
        if (t.type === 'income') {
            months[month].income += t.amount;
        } else {
            months[month].expense += t.amount;
        }
    });
    
    const labels = Object.keys(months).sort();
    const incomeData = labels.map(m => months[m].income);
    const expenseData = labels.map(m => months[m].expense);
    
    const ctx = document.getElementById('incomeExpenseChart');
    if (!ctx) return;
    
    if (incomeExpenseChart) incomeExpenseChart.destroy();
    
    incomeExpenseChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                {
                    label: 'Income',
                    data: incomeData,
                    backgroundColor: '#84fab0'
                },
                {
                    label: 'Expenses',
                    data: expenseData,
                    backgroundColor: '#fa709a'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function updateMonthlyChart() {
    const currentMonth = new Date().toISOString().substring(0, 7);
    const dailyExpenses = {};
    
    allTransactions
        .filter(t => t.type === 'expense' && t.date.substring(0, 7) === currentMonth)
        .forEach(t => {
            dailyExpenses[t.date] = (dailyExpenses[t.date] || 0) + t.amount;
        });
    
    const labels = Object.keys(dailyExpenses).sort();
    const data = labels.map(d => dailyExpenses[d]);
    
    const ctx = document.getElementById('monthlyChart');
    if (!ctx) return;
    
    if (monthlyChart) monthlyChart.destroy();
    
    monthlyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Daily Spending',
                data,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

// Utility Functions
function formatCurrency(amount) {
    return currentCurrency + ' ' + amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

function changeCurrency() {
    currentCurrency = document.getElementById('currencySelect').value;
    localStorage.setItem('currency', currentCurrency);
    updateDashboard();
    updateAnalytics();
}

function showSuccessMessage(message) {
    const div = document.createElement('div');
    div.className = 'success-message';
    div.textContent = message;
    document.body.appendChild(div);
    
    setTimeout(() => div.remove(), 3000);
}

// Data Export/Import
function exportData() {
    if (allTransactions.length === 0) {
        alert('No transactions to export');
        return;
    }
    
    let csv = 'Date,Type,Category,Description,Amount\n';
    allTransactions.forEach(t => {
        csv += `"${t.date}","${t.type}","${t.category}","${t.description}","${t.amount}"\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `expenses_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
}

function importData() {
    document.getElementById('importFile').click();
}

document.getElementById('importFile').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(event) {
        try {
            const csv = event.target.result;
            const lines = csv.split('\n').slice(1);
            
            lines.forEach(line => {
                if (!line.trim()) return;
                const [date, type, category, description, amount] = line.split(',').map(s => s.replace(/"/g, ''));
                
                if (date && type && category && amount) {
                    allTransactions.push({
                        id: Date.now() + Math.random(),
                        date,
                        type,
                        category,
                        description,
                        amount: parseFloat(amount)
                    });
                }
            });
            
            saveData();
            updateDashboard();
            updateAnalytics();
            showSuccessMessage('Data imported successfully!');
        } catch (error) {
            alert('Error importing data: ' + error.message);
        }
    };
    reader.readAsText(file);
});

function clearAllData() {
    if (confirm('Are you absolutely sure? This will delete ALL your data and cannot be undone!')) {
        if (confirm('Final confirmation: Delete all data?')) {
            allTransactions = [];
            allBudgets = [];
            saveData();
            updateDashboard();
            updateAnalytics();
            updateBudgets();
            showSuccessMessage('All data cleared!');
        }
    }
}