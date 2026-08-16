# Industries
INDUSTRIES = [
    'Technology', 'Manufacturing', 'Retail', 'E-Commerce', 'Logistics',
    'Healthcare', 'Finance', 'Education', 'Consulting', 'Food & Beverage',
    'Real Estate', 'Energy', 'Agriculture', 'Other'
]

# Business Types
BUSINESS_TYPES = [
    'Sole Proprietorship', 'Partnership', 'LLC', 'Corporation', 
    'Non-Profit', 'Startup'
]

# Company Sizes
COMPANY_SIZES = ['1-10', '11-50', '51-200', '201-500', '501-1000', '1000+']

# Currencies
CURRENCIES = ['USD', 'EUR', 'GBP', 'INR', 'JPY', 'CNY', 'AUD', 'CAD', 'SGD', 'AED', 'Other']

# Currency Symbols — used globally across all templates
CURRENCY_SYMBOLS = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'INR': '₹',
    'JPY': '¥',
    'CNY': '¥',
    'AUD': 'A$',
    'CAD': 'C$',
    'SGD': 'S$',
    'AED': 'د.إ',
    'Other': '$'
}

# Countries (abbreviated list - full list in form)
COUNTRIES = [
    'United States', 'United Kingdom', 'Canada', 'Australia', 'Germany',
    'France', 'India', 'China', 'Japan', 'Singapore', 'UAE', 'Brazil',
    'Mexico', 'South Korea', 'Italy', 'Spain', 'Netherlands', 'Sweden',
    'Switzerland', 'South Africa', 'Nigeria', 'Kenya', 'Egypt',
    'Saudi Arabia', 'Israel', 'Thailand', 'Malaysia', 'Indonesia',
    'Philippines', 'Vietnam', 'Pakistan', 'Bangladesh', 'Turkey',
    'Russia', 'Poland', 'Ukraine', 'Argentina', 'Chile', 'Colombia',
    'New Zealand', 'Ireland', 'Portugal', 'Greece', 'Czech Republic',
    'Romania', 'Hungary', 'Austria', 'Belgium', 'Denmark', 'Finland',
    'Norway', 'Iceland', 'Other'
]

# Timezones
TIMEZONES = [
    'UTC', 'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles',
    'America/Toronto', 'America/Vancouver', 'America/Mexico_City', 'America/Sao_Paulo',
    'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Madrid', 'Europe/Rome',
    'Europe/Amsterdam', 'Europe/Stockholm', 'Europe/Zurich', 'Europe/Moscow',
    'Asia/Dubai', 'Asia/Kolkata', 'Asia/Singapore', 'Asia/Tokyo', 'Asia/Shanghai',
    'Asia/Hong_Kong', 'Asia/Seoul', 'Asia/Bangkok', 'Asia/Jakarta',
    'Australia/Sydney', 'Australia/Melbourne', 'Pacific/Auckland', 'Africa/Lagos',
    'Africa/Cairo', 'Africa/Johannesburg'
]

# Tax Types
TAX_TYPES = ['GST', 'VAT', 'Sales Tax', 'Income Tax', 'Corporate Tax', 'No Tax']

# User Roles
ROLES = ['Admin', 'Manager', 'Analyst', 'Viewer']

# Simulation Types
SIMULATION_TYPES = [
    'price_increase', 'price_reduction', 'new_branch', 'employee_hiring',
    'employee_layoff', 'inventory_expansion', 'product_launch', 'marketing_campaign',
    'loan_taking', 'investment_planning', 'international_expansion', 'warehouse_expansion',
    'supplier_change', 'tax_changes', 'currency_fluctuation', 'inflation_impact',
    'market_crash', 'competitor_entry', 'economic_recession', 'customer_growth',
    'demand_growth', 'supply_disruption'
]

SIMULATION_LABELS = {
    'price_increase': 'Price Increase',
    'price_reduction': 'Price Reduction',
    'new_branch': 'New Branch Opening',
    'employee_hiring': 'Employee Hiring',
    'employee_layoff': 'Employee Layoff',
    'inventory_expansion': 'Inventory Expansion',
    'product_launch': 'New Product Launch',
    'marketing_campaign': 'Marketing Campaign',
    'loan_taking': 'Loan Taking',
    'investment_planning': 'Investment Planning',
    'international_expansion': 'International Expansion',
    'warehouse_expansion': 'Warehouse Expansion',
    'supplier_change': 'Supplier Change',
    'tax_changes': 'Tax Changes',
    'currency_fluctuation': 'Currency Fluctuation',
    'inflation_impact': 'Inflation Impact',
    'market_crash': 'Market Crash',
    'competitor_entry': 'Competitor Entry',
    'economic_recession': 'Economic Recession',
    'customer_growth': 'Customer Growth',
    'demand_growth': 'Demand Growth',
    'supply_disruption': 'Supply Disruption'
}

# Risk Categories
RISK_CATEGORIES = [
    'financial', 'operational', 'market', 'supply_chain', 'inventory',
    'growth', 'competition', 'economic', 'cashflow'
]

RISK_LABELS = {
    'financial': 'Financial Risk',
    'operational': 'Operational Risk',
    'market': 'Market Risk',
    'supply_chain': 'Supply Chain Risk',
    'inventory': 'Inventory Risk',
    'growth': 'Growth Risk',
    'competition': 'Competition Risk',
    'economic': 'Economic Risk',
    'cashflow': 'Cash Flow Risk'
}

# Forecast Types
FORECAST_TYPES = [
    'revenue', 'profit', 'demand', 'customer', 'market',
    'cashflow', 'expense', 'expansion', 'risk', 'opportunity'
]

FORECAST_LABELS = {
    'revenue': 'Revenue Forecast',
    'profit': 'Profit Forecast',
    'demand': 'Demand Forecast',
    'customer': 'Customer Growth Forecast',
    'market': 'Market Growth Forecast',
    'cashflow': 'Cash Flow Forecast',
    'expense': 'Expense Forecast',
    'expansion': 'Expansion Forecast',
    'risk': 'Risk Forecast',
    'opportunity': 'Opportunity Forecast'
}

# Forecast Methods
FORECAST_METHODS = [
    'moving_average', 'exponential_smoothing', 'arima', 'prophet', 'linear_regression'
]

# Forecast Horizons (in days)
FORECAST_HORIZONS = [30, 90, 180, 365, 1095, 1825]

# Report Types
REPORT_TYPES = [
    'executive', 'board', 'investor', 'risk', 'growth',
    'forecast', 'financial', 'operational', 'department'
]

REPORT_LABELS = {
    'executive': 'Executive Report',
    'board': 'Board Report',
    'investor': 'Investor Report',
    'risk': 'Risk Report',
    'growth': 'Growth Report',
    'forecast': 'Forecast Report',
    'financial': 'Financial Report',
    'operational': 'Operational Report',
    'department': 'Department Report'
}

# Document Types
DOCUMENT_TYPES = ['pdf', 'csv', 'xlsx', 'xls', 'docx', 'txt', 'json', 'xml', 'png', 'jpg', 'jpeg', 'gif', 'zip']

# Department defaults
DEFAULT_DEPARTMENTS = ['Sales', 'Marketing', 'Operations', 'Finance', 'HR', 'IT']

# Security Questions
SECURITY_QUESTIONS = [
    "What was your childhood nickname?",
    "What is the name of your first pet?",
    "What was your first car?",
    "What elementary school did you attend?",
    "What is your mother's maiden name?",
    "What is your favorite movie?",
    "What city were you born in?",
    "What is your favorite book?"
]

# Pagination options
PAGINATION_OPTIONS = [10, 25, 50, 100]

# Health score thresholds
HEALTH_SCORE_THRESHOLDS = {
    'critical': 40,
    'warning': 70,
    'good': 90
}

# Score colors
SCORE_COLORS = {
    'critical': '#EF4444',
    'warning': '#F59E0B',
    'good': '#10B981',
    'excellent': '#059669'
}