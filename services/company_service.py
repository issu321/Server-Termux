from database.db import db
from database.models.company import Company
from database.models.company_payments import CompanyPayments
from database.models.department import Department
from database.models.branch import Branch
from config.constants import DEFAULT_DEPARTMENTS

class CompanyService:

    @staticmethod
    def _fmt_money(amount, currency_symbol='$'):
        """Format a monetary amount with the given currency symbol."""
        return f"{currency_symbol}{abs(amount):,.2f}"

    @staticmethod
    def create_company(data):
        annual_revenue = data.get('annual_revenue', 0.0) or 0.0
        # Initial equity proxy: 30% of annual revenue (typical for SMEs)
        # or user-provided value
        initial_equity = data.get('total_equity', annual_revenue * 0.3)
        initial_debt = data.get('total_debt', 0.0)

        company = Company(
            company_name=data.get('company_name'),
            business_name=data.get('business_name'),
            owner_name=data.get('owner_name'),
            ceo_name=data.get('ceo_name'),
            industry=data.get('industry'),
            business_type=data.get('business_type'),
            description=data.get('description'),
            company_size=data.get('company_size'),
            employee_count=data.get('employee_count', 0),
            annual_revenue=annual_revenue,
            total_equity=initial_equity,
            total_debt=initial_debt,
            currency=data.get('currency', 'USD'),
            country=data.get('country'),
            city=data.get('city'),
            timezone=data.get('timezone', 'UTC'),
            tax_type=data.get('tax_type'),
            tax_rate=data.get('tax_rate', 0.0),
            website=data.get('website'),
            email=data.get('email'),
            mobile=data.get('mobile'),
            whatsapp=data.get('whatsapp'),
            telegram=data.get('telegram')
        )
        db.session.add(company)
        db.session.commit()

        # Create default departments
        for dept_name in DEFAULT_DEPARTMENTS:
            dept = Department(
                company_id=company.id,
                name=dept_name,
                code=dept_name.upper()[:3],
                budget=company.annual_revenue * 0.1 if company.annual_revenue else 0
            )
            db.session.add(dept)

        # Create main branch
        branch = Branch(
            company_id=company.id,
            name=f"{company.company_name} - Main Office",
            city=company.city,
            country=company.country,
            is_main=True,
            branch_type='headquarters'
        )
        db.session.add(branch)
        db.session.commit()

        return company

    @staticmethod
    def get_company(company_id):
        return Company.query.get(company_id)

    @staticmethod
    def company_exists():
        return Company.query.first() is not None

    @staticmethod
    def save_payments(company_id, data):
        payments = CompanyPayments.query.filter_by(company_id=company_id).first()
        if not payments:
            payments = CompanyPayments(company_id=company_id)
            db.session.add(payments)

        for key, value in data.items():
            if hasattr(payments, key):
                setattr(payments, key, value)

        db.session.commit()
        return payments

    @staticmethod
    def update_company(company_id, data):
        company = Company.query.get(company_id)
        if not company:
            return None

        for key, value in data.items():
            if hasattr(company, key):
                setattr(company, key, value)

        db.session.commit()
        return company

    @staticmethod
    def update_financials(company_id, equity=None, debt=None):
        """Update company total equity and/or total debt."""
        company = Company.query.get(company_id)
        if not company:
            return None
        if equity is not None:
            company.total_equity = float(equity)
        if debt is not None:
            company.total_debt = float(debt)
        db.session.commit()
        return company

    @staticmethod
    def get_company_financials(company_id):
        """Get equity, debt, and computed ratios for a company."""
        company = Company.query.get(company_id)
        if not company:
            return None
        equity = getattr(company, 'total_equity', 0.0) or 0.0
        debt = getattr(company, 'total_debt', 0.0) or 0.0
        revenue = company.annual_revenue or 0.0
        # Fallback equity proxy if not set
        if equity <= 0 and revenue > 0:
            equity = revenue * 0.3
        if equity <= 0:
            equity = 100000.0
        return {
            'total_equity': equity,
            'total_debt': debt,
            'debt_equity_ratio': round(debt / equity, 4) if equity > 0 else 0.0,
            'annual_revenue': revenue
        }