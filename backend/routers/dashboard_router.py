from fastapi import APIRouter
from backend.models import DashboardStats, DashboardReports
from backend.database import get_dashboard_stats, get_dashboard_reports

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_stats():
    """Retrieve key metrics for upcoming events, past events, registrations, and users."""
    return get_dashboard_stats()


@router.get("/reports", response_model=DashboardReports)
def get_reports():
    """Retrieve event participant breakdown and recent registrations for reporting."""
    return get_dashboard_reports()
