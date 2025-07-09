from django.shortcuts import redirect


def home_redirect(request):
    """Redirect users to hotel home page"""
    return redirect('home')