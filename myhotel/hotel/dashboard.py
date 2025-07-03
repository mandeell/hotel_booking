from django.shortcuts import render
from .models import Booking
from django.db.models.functions import TruncDay, TruncMonth, TruncYear, ExtractWeek, ExtractYear, ExtractMonth
from django.db.models import Count, Q
from django.utils import timezone
import calendar


def dashboard_view(request):
    now = timezone.now()
    today = now.date()
    current_year = now.year
    current_month = now.month
    current_week = now.isocalendar()[1]

    # Helper to aggregate by status
    def status_counts(queryset, group_by):
        base = queryset.values(group_by)
        return list(base.annotate(
            confirmed=Count('id', filter=Q(status='confirmed')),
            pending=Count('id', filter=Q(status='pending')),
            cancelled=Count('id', filter=Q(status='cancelled')),
        ))

    # Bookings for today
    bookings_per_day = Booking.objects.filter(created_at__date=today) \
        .annotate(day=TruncDay('created_at')) \
        .values('day') \
        .annotate(
            confirmed=Count('id', filter=Q(status='confirmed')),
            pending=Count('id', filter=Q(status='pending')),
            cancelled=Count('id', filter=Q(status='cancelled')),
        ) \
        .order_by('day')
    bookings_per_day = [
        {**item, 'label': item['day'].strftime('%A, %B %d, %Y') if item['day'] else ''}
        for item in bookings_per_day
    ]

    # Calculate current week range (Monday to Sunday)
    week_start = today - timezone.timedelta(days=today.weekday())
    week_end = week_start + timezone.timedelta(days=6)
    week_label = f"{week_start.strftime('%A, %B %d, %Y')} - {week_end.strftime('%A, %B %d, %Y')}"

    # Bookings for current week
    bookings_per_week = Booking.objects.filter(created_at__date__gte=week_start, created_at__date__lte=week_end) \
        .annotate(week=ExtractWeek('created_at'), year=ExtractYear('created_at')) \
        .values('year', 'week') \
        .annotate(
            confirmed=Count('id', filter=Q(status='confirmed')),
            pending=Count('id', filter=Q(status='pending')),
            cancelled=Count('id', filter=Q(status='cancelled')),
        ) \
        .order_by('year', 'week')
    bookings_per_week = [
        {**item, 'label': week_label}
        for item in bookings_per_week
    ]

    # Bookings for current month
    bookings_per_month = Booking.objects.annotate(month=TruncMonth('created_at')) \
        .filter(created_at__year=current_year, created_at__month=current_month) \
        .values('month') \
        .annotate(
            confirmed=Count('id', filter=Q(status='confirmed')),
            pending=Count('id', filter=Q(status='pending')),
            cancelled=Count('id', filter=Q(status='cancelled')),
        ) \
        .order_by('month')
    bookings_per_month = [
        {**item, 'label': item['month'].strftime('%B') if item['month'] else ''}
        for item in bookings_per_month
    ]

    # Bookings for current year
    bookings_per_year = Booking.objects.annotate(year=TruncYear('created_at')) \
        .filter(created_at__year=current_year) \
        .values('year') \
        .annotate(
            confirmed=Count('id', filter=Q(status='confirmed')),
            pending=Count('id', filter=Q(status='pending')),
            cancelled=Count('id', filter=Q(status='cancelled')),
        ) \
        .order_by('year')
    bookings_per_year = [
        {**item, 'label': str(item['year'].year) if item['year'] else ''}
        for item in bookings_per_year
    ]

    # All bookings (total counts by status)
    all_bookings_qs = Booking.objects.all()
    all_bookings = [{
        'label': 'All Bookings',
        'confirmed': all_bookings_qs.filter(status='confirmed').count(),
        'pending': all_bookings_qs.filter(status='pending').count(),
        'cancelled': all_bookings_qs.filter(status='cancelled').count(),
    }]

    context = {
        'bookings_per_day': list(bookings_per_day),
        'bookings_per_week': list(bookings_per_week),
        'bookings_per_month': list(bookings_per_month),
        'bookings_per_year': list(bookings_per_year),
        'all_bookings': all_bookings,
    }
    return render(request, 'custom_admin/dashboard.html', context)
