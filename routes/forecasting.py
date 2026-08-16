from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from flask_login import login_required, current_user
from database.models.forecast import Forecast, ForecastResult
from services.forecast_service import ForecastService
from datetime import datetime
from config.constants import CURRENCY_SYMBOLS

forecasting_bp = Blueprint('forecasting', __name__)

# Robust fallback defaults in case config/constants.py is missing or empty
DEFAULT_FORECAST_TYPES = ['revenue', 'expenses', 'profit', 'customers', 'inventory']
DEFAULT_FORECAST_LABELS = {
    'revenue': 'Revenue Forecast',
    'expenses': 'Expense Forecast', 
    'profit': 'Profit Forecast',
    'customers': 'Customer Growth',
    'inventory': 'Inventory Demand'
}
DEFAULT_METHODS = ['prophet', 'moving_average', 'linear_regression', 'exponential_smoothing', 'arima']
DEFAULT_HORIZONS = [7, 14, 30, 60, 90, 180, 365]

def _get_forecast_config():
    """Safely load forecast configuration with fallbacks."""
    try:
        from config.constants import FORECAST_TYPES, FORECAST_LABELS, FORECAST_METHODS, FORECAST_HORIZONS
        return (
            FORECAST_TYPES or DEFAULT_FORECAST_TYPES,
            FORECAST_LABELS or DEFAULT_FORECAST_LABELS,
            FORECAST_METHODS or DEFAULT_METHODS,
            FORECAST_HORIZONS or DEFAULT_HORIZONS
        )
    except Exception:
        return DEFAULT_FORECAST_TYPES, DEFAULT_FORECAST_LABELS, DEFAULT_METHODS, DEFAULT_HORIZONS

def _get_currency_symbol():
    """Get currency symbol from session or fallback to CURRENCY_SYMBOLS."""
    if 'currency_symbol' in session:
        return session['currency_symbol']
    currency = session.get('company_currency', 'USD')
    return CURRENCY_SYMBOLS.get(currency, '$')


@forecasting_bp.route('/')
@login_required
def index():
    company_id = session.get('company_id')
    forecasts = Forecast.query.filter_by(company_id=company_id).order_by(Forecast.created_at.desc()).limit(50).all()
    
    ft, fl, m, h = _get_forecast_config()
    currency_symbol = _get_currency_symbol()
    
    return render_template('forecasting/forecast_lab.html', 
                         forecasts=forecasts,
                         forecast_types=ft,
                         forecast_labels=fl,
                         methods=m,
                         horizons=h,
                         view_forecast=None,
                         results=None,
                         currency_symbol=currency_symbol)

@forecasting_bp.route('/run', methods=['POST'])
@login_required
def run_forecast():
    company_id = session.get('company_id')
    forecast_type = request.form.get('forecast_type', 'revenue')
    method = request.form.get('method', 'prophet')
    horizon = int(request.form.get('horizon_days', 90))
    name = request.form.get('name', '').strip()
    currency_symbol = _get_currency_symbol()
    
    if not name:
        _, fl, _, _ = _get_forecast_config()
        name = f"{fl.get(forecast_type, 'Forecast').title()} - {datetime.now().strftime('%Y-%m-%d')}"
    
    forecast = ForecastService.generate_forecast(
        company_id, current_user.id, forecast_type, method, horizon, name, currency_symbol=currency_symbol
    )
    
    flash(f'Forecast "{name}" generated successfully!', 'success')
    return redirect(url_for('forecasting.view', forecast_id=forecast.id))

@forecasting_bp.route('/view/<int:forecast_id>')
@login_required
def view(forecast_id):
    company_id = session.get('company_id')
    forecast = Forecast.query.get_or_404(forecast_id)
    if forecast.company_id != company_id:
        flash('Access denied', 'danger')
        return redirect(url_for('forecasting.index'))
    
    results = ForecastResult.query.filter_by(forecast_id=forecast_id).order_by(ForecastResult.date).all()
    
    # Always pass form dropdown data so the "New Forecast" form works on the view page too
    ft, fl, m, h = _get_forecast_config()
    currency_symbol = _get_currency_symbol()
    
    # Calculate summary statistics for enhanced UI
    summary = _calculate_summary(results, forecast)
    
    return render_template('forecasting/forecast_lab.html', 
                         view_forecast=forecast, 
                         results=results,
                         forecasts=Forecast.query.filter_by(company_id=company_id).order_by(Forecast.created_at.desc()).limit(50).all(),
                         forecast_types=ft,
                         forecast_labels=fl,
                         methods=m,
                         horizons=h,
                         summary=summary,
                         currency_symbol=currency_symbol)

@forecasting_bp.route('/api/data/<int:forecast_id>')
@login_required
def api_data(forecast_id):
    forecast = Forecast.query.get_or_404(forecast_id)
    if forecast.company_id != session.get('company_id'):
        return jsonify({'error': 'Access denied'}), 403
    
    results = ForecastResult.query.filter_by(forecast_id=forecast_id).order_by(ForecastResult.date).all()
    return jsonify({
        'forecast': forecast.to_dict(),
        'data': [{
            'date': r.date.isoformat(),
            'value': r.value,
            'lower': r.lower_bound,
            'upper': r.upper_bound
        } for r in results]
    })


def _calculate_summary(results, forecast):
    """Generate human-readable summary statistics from forecast results."""
    if not results or len(results) < 2:
        return None
    
    values = [r.value for r in results]
    lowers = [r.lower_bound for r in results if r.lower_bound is not None]
    uppers = [r.upper_bound for r in results if r.upper_bound is not None]
    
    first_val = values[0]
    last_val = values[-1]
    change = last_val - first_val
    change_pct = (change / first_val * 100) if first_val != 0 else 0
    
    avg_val = sum(values) / len(values)
    max_val = max(values)
    min_val = min(values)
    
    trend = "upward" if last_val > first_val else "downward" if last_val < first_val else "stable"
    volatility = ((max_val - min_val) / avg_val * 100) if avg_val != 0 else 0
    
    confidence_width = 0
    if lowers and uppers:
        avg_width = sum(u - l for u, l in zip(uppers, lowers)) / len(lowers)
        confidence_width = (avg_width / avg_val * 100) if avg_val != 0 else 0
    
    # Determine recommendation
    if trend == "upward" and change_pct > 10:
        recommendation = "Strong positive trend detected. Consider increasing inventory and marketing spend to capture growth."
    elif trend == "upward":
        recommendation = "Moderate growth expected. Maintain current operations while monitoring key metrics."
    elif trend == "downward" and change_pct < -10:
        recommendation = "Significant decline projected. Review cost structure and consider corrective strategies immediately."
    elif trend == "downward":
        recommendation = "Slight contraction ahead. Focus on retention and efficiency improvements."
    else:
        recommendation = "Stable period expected. Good time for optimization and strategic planning."
    
    return {
        'first_value': first_val,
        'last_value': last_val,
        'change': change,
        'change_pct': change_pct,
        'trend': trend,
        'volatility': volatility,
        'confidence_width': confidence_width,
        'average': avg_val,
        'max': max_val,
        'min': min_val,
        'recommendation': recommendation,
        'direction_icon': '↑' if trend == 'upward' else '↓' if trend == 'downward' else '→',
        'direction_color': 'success' if trend == 'upward' else 'danger' if trend == 'downward' else 'warning'
    }