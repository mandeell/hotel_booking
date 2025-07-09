from django.views.generic import TemplateView
from ..models import Booking
from django.db.models.functions import TruncDay, TruncMonth, TruncYear, ExtractWeek, ExtractYear, ExtractMonth
from django.db.models import Count, Q
from django.utils import timezone
import calendar

class DashboardView(TemplateView):
    template_name = 'admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        today = now.date()
        current_year = now.year
        current_month = now.month
        current_week = now.isocalendar()[1]

        # Bookings for today
        bookings_today_qs = Booking.objects.filter(created_at__date=today)
        bookings_today = {
            'confirmed': bookings_today_qs.filter(status='confirmed').count(),
            'pending': bookings_today_qs.filter(status='pending').count(),
            'cancelled': bookings_today_qs.filter(status='cancelled').count(),
        }
        bookings_today['total'] = sum(bookings_today.values())

        # Bookings for current month
        bookings_month_qs = Booking.objects.filter(created_at__year=current_year, created_at__month=current_month)
        bookings_month = {
            'confirmed': bookings_month_qs.filter(status='confirmed').count(),
            'pending': bookings_month_qs.filter(status='pending').count(),
            'cancelled': bookings_month_qs.filter(status='cancelled').count(),
        }
        bookings_month['total'] = sum(bookings_month.values())

        # Bookings for current year
        bookings_year_qs = Booking.objects.filter(created_at__year=current_year)
        bookings_year = {
            'confirmed': bookings_year_qs.filter(status='confirmed').count(),
            'pending': bookings_year_qs.filter(status='pending').count(),
            'cancelled': bookings_year_qs.filter(status='cancelled').count(),
        }
        bookings_year['total'] = sum(bookings_year.values())

        # All bookings (total counts by status)
        all_bookings_qs = Booking.objects.all()
        all_bookings = {
            'confirmed': all_bookings_qs.filter(status='confirmed').count(),
            'pending': all_bookings_qs.filter(status='pending').count(),
            'cancelled': all_bookings_qs.filter(status='cancelled').count(),
        }
        all_bookings['total'] = sum(all_bookings.values())

        context.update({
            'bookings_today': bookings_today,
            'bookings_month': bookings_month,
            'bookings_year': bookings_year,
            'all_bookings': all_bookings,
        })
        return context
