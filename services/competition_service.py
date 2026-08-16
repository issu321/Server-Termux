from database.db import db
from database.models.competitor import Competitor
from database.models.company import Company
from sqlalchemy import func
import random

class CompetitionService:
    """Auto-generates and analyzes competitive landscape for a company."""

    COMPETITOR_TEMPLATES = {
        'Technology': [
            {'name': 'NexGen Solutions', 'position': 'Market Leader', 'base_share': 18.5, 'size_mult': 2.5},
            {'name': 'CloudFirst Inc', 'position': 'Challenger', 'base_share': 12.3, 'size_mult': 1.8},
            {'name': 'DevStack Labs', 'position': 'Niche Player', 'base_share': 4.2, 'size_mult': 0.6},
            {'name': 'ByteForge Systems', 'position': 'Emerging', 'base_share': 2.8, 'size_mult': 0.4},
        ],
        'Manufacturing': [
            {'name': 'IndustrialCore Corp', 'position': 'Market Leader', 'base_share': 22.1, 'size_mult': 3.2},
            {'name': 'PrecisionWorks Ltd', 'position': 'Challenger', 'base_share': 14.7, 'size_mult': 2.1},
            {'name': 'EcoMakers Alliance', 'position': 'Niche Player', 'base_share': 5.5, 'size_mult': 0.7},
            {'name': 'RapidFab Industries', 'position': 'Emerging', 'base_share': 3.1, 'size_mult': 0.5},
        ],
        'Retail': [
            {'name': 'MegaMart Global', 'position': 'Market Leader', 'base_share': 28.4, 'size_mult': 4.5},
            {'name': 'ShopDirect Co', 'position': 'Challenger', 'base_share': 15.2, 'size_mult': 2.3},
            {'name': 'BoutiqueHub', 'position': 'Niche Player', 'base_share': 3.8, 'size_mult': 0.5},
            {'name': 'QuickBuy Express', 'position': 'Emerging', 'base_share': 2.4, 'size_mult': 0.4},
        ],
        'E-Commerce': [
            {'name': 'GlobalCart Inc', 'position': 'Market Leader', 'base_share': 25.6, 'size_mult': 3.8},
            {'name': 'SwiftMarket', 'position': 'Challenger', 'base_share': 13.9, 'size_mult': 2.0},
            {'name': 'ShopifyRival', 'position': 'Niche Player', 'base_share': 4.5, 'size_mult': 0.6},
            {'name': 'MicroStore Network', 'position': 'Emerging', 'base_share': 1.9, 'size_mult': 0.3},
        ],
        'Healthcare': [
            {'name': 'MediCare Systems', 'position': 'Market Leader', 'base_share': 19.8, 'size_mult': 2.9},
            {'name': 'HealthFirst Tech', 'position': 'Challenger', 'base_share': 11.4, 'size_mult': 1.7},
            {'name': 'BioNova Labs', 'position': 'Niche Player', 'base_share': 3.9, 'size_mult': 0.5},
            {'name': 'CureFast Inc', 'position': 'Emerging', 'base_share': 2.1, 'size_mult': 0.3},
        ],
        'Finance': [
            {'name': 'CapitalTrust Bank', 'position': 'Market Leader', 'base_share': 21.3, 'size_mult': 3.5},
            {'name': 'FinEdge Partners', 'position': 'Challenger', 'base_share': 12.8, 'size_mult': 1.9},
            {'name': 'MicroLend Pro', 'position': 'Niche Player', 'base_share': 4.1, 'size_mult': 0.6},
            {'name': 'CryptoVault Inc', 'position': 'Emerging', 'base_share': 1.7, 'size_mult': 0.25},
        ],
        'Logistics': [
            {'name': 'FastFreight Global', 'position': 'Market Leader', 'base_share': 17.9, 'size_mult': 2.7},
            {'name': 'RouteMaster Corp', 'position': 'Challenger', 'base_share': 10.5, 'size_mult': 1.6},
            {'name': 'LastMile Pro', 'position': 'Niche Player', 'base_share': 5.2, 'size_mult': 0.7},
            {'name': 'DroneShip Inc', 'position': 'Emerging', 'base_share': 2.6, 'size_mult': 0.4},
        ],
        'Education': [
            {'name': 'EduWorld Global', 'position': 'Market Leader', 'base_share': 16.2, 'size_mult': 2.4},
            {'name': 'LearnFast Academy', 'position': 'Challenger', 'base_share': 9.7, 'size_mult': 1.5},
            {'name': 'SkillForge', 'position': 'Niche Player', 'base_share': 3.5, 'size_mult': 0.5},
            {'name': 'NanoLearn Labs', 'position': 'Emerging', 'base_share': 1.8, 'size_mult': 0.3},
        ],
        'Consulting': [
            {'name': 'StrategyFirst Partners', 'position': 'Market Leader', 'base_share': 15.4, 'size_mult': 2.2},
            {'name': 'AdvisoryCore Inc', 'position': 'Challenger', 'base_share': 8.9, 'size_mult': 1.4},
            {'name': 'NicheConsult Pro', 'position': 'Niche Player', 'base_share': 4.8, 'size_mult': 0.6},
            {'name': 'AgileMinds Group', 'position': 'Emerging', 'base_share': 2.3, 'size_mult': 0.35},
        ],
        'Food & Beverage': [
            {'name': 'GourmetChain Corp', 'position': 'Market Leader', 'base_share': 20.1, 'size_mult': 3.1},
            {'name': 'FreshDirect Co', 'position': 'Challenger', 'base_share': 11.6, 'size_mult': 1.8},
            {'name': 'OrganicEats Ltd', 'position': 'Niche Player', 'base_share': 4.3, 'size_mult': 0.6},
            {'name': 'QuickBite Labs', 'position': 'Emerging', 'base_share': 2.0, 'size_mult': 0.3},
        ],
        'Real Estate': [
            {'name': 'PrimeProperty Group', 'position': 'Market Leader', 'base_share': 14.8, 'size_mult': 2.3},
            {'name': 'UrbanSpace Inc', 'position': 'Challenger', 'base_share': 9.2, 'size_mult': 1.5},
            {'name': 'EcoLiving Dev', 'position': 'Niche Player', 'base_share': 3.7, 'size_mult': 0.5},
            {'name': 'PropTech Ventures', 'position': 'Emerging', 'base_share': 1.6, 'size_mult': 0.25},
        ],
        'Energy': [
            {'name': 'PowerGrid International', 'position': 'Market Leader', 'base_share': 23.5, 'size_mult': 3.6},
            {'name': 'GreenWatt Energy', 'position': 'Challenger', 'base_share': 13.1, 'size_mult': 2.0},
            {'name': 'SolarNova Corp', 'position': 'Niche Player', 'base_share': 5.8, 'size_mult': 0.8},
            {'name': 'FusionFuture Inc', 'position': 'Emerging', 'base_share': 2.2, 'size_mult': 0.3},
        ],
        'Agriculture': [
            {'name': 'AgriGlobal Corp', 'position': 'Market Leader', 'base_share': 18.7, 'size_mult': 2.8},
            {'name': 'CropMax Systems', 'position': 'Challenger', 'base_share': 10.4, 'size_mult': 1.6},
            {'name': 'OrganicHarvest Co', 'position': 'Niche Player', 'base_share': 4.6, 'size_mult': 0.6},
            {'name': 'SmartFarm Tech', 'position': 'Emerging', 'base_share': 2.1, 'size_mult': 0.35},
        ],
    }

    DEFAULT_COMPETITORS = [
        {'name': 'AlphaCorp Industries', 'position': 'Market Leader', 'base_share': 20.0, 'size_mult': 3.0},
        {'name': 'Beta Solutions Ltd', 'position': 'Challenger', 'base_share': 12.0, 'size_mult': 1.8},
        {'name': 'Gamma Ventures', 'position': 'Niche Player', 'base_share': 4.0, 'size_mult': 0.5},
        {'name': 'Delta Innovations', 'position': 'Emerging', 'base_share': 2.0, 'size_mult': 0.3},
    ]

    @staticmethod
    def get_or_create_competitors(company_id):
        """Fetch existing competitors or auto-generate realistic ones."""
        existing = Competitor.query.filter_by(company_id=company_id).order_by(
            Competitor.market_share.desc()
        ).all()

        if existing:
            return existing

        return CompetitionService._generate_competitors(company_id)

    @staticmethod
    def _generate_competitors(company_id):
        """Generate realistic competitor profiles based on company profile."""
        company = Company.query.get(company_id)
        if not company:
            return []

        industry = company.industry or 'Other'
        company_revenue = company.annual_revenue or 1000000
        company_employees = company.employee_count or 50

        templates = CompetitionService.COMPETITOR_TEMPLATES.get(
            industry, CompetitionService.DEFAULT_COMPETITORS
        )

        # Select 3-4 competitors (not all templates)
        selected = random.sample(templates, min(len(templates), random.randint(3, 4)))
        competitors = []

        total_competitor_share = 0

        for template in selected:
            # Add randomness so it's not identical every time
            share = template['base_share'] * random.uniform(0.85, 1.15)
            share = round(share, 1)
            total_competitor_share += share

            revenue = company_revenue * template['size_mult'] * random.uniform(0.9, 1.1)
            employees = max(1, int(company_employees * template['size_mult'] * random.uniform(0.8, 1.2)))

            # Determine threat level based on relative size
            revenue_ratio = revenue / max(company_revenue, 1)
            if revenue_ratio > 2.0:
                threat = 'high'
            elif revenue_ratio > 0.8:
                threat = 'medium'
            else:
                threat = 'low'

            comp = Competitor(
                company_id=company_id,
                name=template['name'],
                threat_level=threat,
                market_share=share,
                revenue_estimate=round(revenue, 0),
                employee_count=employees,
                market_position=template['position'],
                industry=industry,
                website=f"https://{template['name'].lower().replace(' ', '').replace('.', '').replace('&', 'and')}.com",
                strengths=CompetitionService._generate_strengths(template['position']),
                weaknesses=CompetitionService._generate_weaknesses(template['position']),
                pricing_strategy=CompetitionService._generate_pricing(template['position'])
                # REMOVED: customer_overlap=random.randint(15, 85)  -- field doesn't exist on model
            )
            db.session.add(comp)
            competitors.append(comp)

        db.session.commit()
        return competitors

    @staticmethod
    def _generate_strengths(position):
        strengths = {
            'Market Leader': 'Brand recognition, economies of scale, established distribution, deep R&D budget',
            'Challenger': 'Aggressive pricing, rapid innovation, strong marketing, expanding market share',
            'Niche Player': 'Specialized expertise, loyal customer base, premium positioning, high margins',
            'Emerging': 'Cutting-edge technology, agile operations, low overhead, disruptive model'
        }
        return strengths.get(position, 'Strong market presence')

    @staticmethod
    def _generate_weaknesses(position):
        weaknesses = {
            'Market Leader': 'Bureaucratic inertia, legacy systems, slow to adapt, high overhead',
            'Challenger': 'Limited resources, brand recognition gaps, dependency on funding, operational strain',
            'Niche Player': 'Limited scale, vulnerability to market shifts, narrow product range',
            'Emerging': 'Unproven track record, limited capital, high burn rate, customer acquisition costs'
        }
        return weaknesses.get(position, 'Scaling challenges')

    @staticmethod
    def _generate_pricing(position):
        pricing = {
            'Market Leader': 'Premium / Value-based',
            'Challenger': 'Competitive / Penetration',
            'Niche Player': 'Premium / Skimming',
            'Emerging': 'Freemium / Low-margin'
        }
        return pricing.get(position, 'Market-rate')

    @staticmethod
    def get_competition_summary(company_id):
        """Build comprehensive competitive analysis summary."""
        competitors = CompetitionService.get_or_create_competitors(company_id)
        company = Company.query.get(company_id)

        if not competitors or not company:
            return None

        company_revenue = company.annual_revenue or 1000000
        company_employees = company.employee_count or 50

        # Calculate total market size from competitors + company
        total_competitor_revenue = sum(c.revenue_estimate or 0 for c in competitors)
        # Assume company + competitors represent ~65-75% of total market (rest is fragmented)
        total_market = (company_revenue + total_competitor_revenue) / random.uniform(0.65, 0.75)

        # Company's implied market share
        company_share = (company_revenue / total_market) * 100 if total_market else 0

        # Ranking
        all_revenues = [(c.name, c.revenue_estimate or 0) for c in competitors] + [
            (company.company_name or 'Your Company', company_revenue)
        ]
        all_revenues.sort(key=lambda x: x[1], reverse=True)
        company_rank = next((i + 1 for i, (name, _) in enumerate(all_revenues)
                            if name == (company.company_name or 'Your Company')), len(all_revenues))

        total_competitors = len(competitors)
        high_threats = sum(1 for c in competitors if c.threat_level == 'high')
        medium_threats = sum(1 for c in competitors if c.threat_level == 'medium')
        low_threats = sum(1 for c in competitors if c.threat_level == 'low')

        # Largest competitor
        leader = max(competitors, key=lambda c: c.revenue_estimate or 0)
        revenue_gap = (leader.revenue_estimate or 0) - company_revenue
        gap_pct = (revenue_gap / max(company_revenue, 1)) * 100

        # Average competitor metrics
        avg_comp_revenue = total_competitor_revenue / total_competitors
        avg_comp_employees = sum(c.employee_count or 0 for c in competitors) / total_competitors
        avg_comp_share = sum(c.market_share or 0 for c in competitors) / total_competitors

        # Competitive intensity
        total_tracked_share = sum(c.market_share or 0 for c in competitors) + company_share
        if total_tracked_share > 80:
            intensity = 'High'
            intensity_desc = 'The market is highly concentrated. Gaining share requires direct share capture from established players.'
            intensity_color = 'danger'
        elif total_tracked_share > 50:
            intensity = 'Moderate'
            intensity_desc = 'Fragmented market with room for growth, but key players are already staking claims.'
            intensity_color = 'warning'
        else:
            intensity = 'Low'
            intensity_desc = 'Highly fragmented market. Growth can come from capturing unclaimed demand rather than direct competition.'
            intensity_color = 'success'

        # Strategic recommendation
        if company_rank == 1:
            position_advice = "You are the revenue leader in this tracked set. Focus on margin defense and ecosystem lock-in."
        elif company_rank <= 3:
            position_advice = f"You rank #{company_rank} among tracked competitors. Focus on differentiation to close the gap with the leader."
        else:
            position_advice = f"You rank #{company_rank}. Consider niche specialization or acquisition to accelerate market position."

        if high_threats > 0:
            threat_advice = f"{high_threats} high-threat competitor(s) detected. Monitor their pricing and product roadmap closely."
        elif medium_threats > 0:
            threat_advice = f"{medium_threats} medium-threat competitor(s). Maintain competitive parity while investing in differentiation."
        else:
            threat_advice = "Low immediate threat from tracked competitors. Good window for aggressive growth investment."

        return {
            'competitors': competitors,
            'total_market': round(total_market, 0),
            'company_revenue': company_revenue,
            'company_employees': company_employees,
            'company_share': round(company_share, 2),
            'company_rank': company_rank,
            'total_competitors': total_competitors,
            'high_threats': high_threats,
            'medium_threats': medium_threats,
            'low_threats': low_threats,
            'market_leader': leader,
            'revenue_gap': round(revenue_gap, 0),
            'gap_pct': round(gap_pct, 1),
            'avg_comp_revenue': round(avg_comp_revenue, 0),
            'avg_comp_employees': round(avg_comp_employees, 0),
            'avg_comp_share': round(avg_comp_share, 1),
            'intensity': intensity,
            'intensity_desc': intensity_desc,
            'intensity_color': intensity_color,
            'position_advice': position_advice,
            'threat_advice': threat_advice,
            'total_tracked_share': round(total_tracked_share, 1),
            'generated_at': __import__('datetime').datetime.utcnow().strftime('%B %d, %Y')
        }

    @staticmethod
    def refresh_competitors(company_id):
        """Clear and regenerate competitor data."""
        Competitor.query.filter_by(company_id=company_id).delete()
        db.session.commit()
        return CompetitionService._generate_competitors(company_id)