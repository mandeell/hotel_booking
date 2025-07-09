from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import requests
import json
from .models import Booking, Guest, RoomType, Room
from decimal import Decimal
from datetime import date
import logging

logger = logging.getLogger(__name__)

@require_POST
def submit_booking(request):
    if request.method != 'POST':
        logger.warning("Invalid request method for submit_booking")
        return JsonResponse({'success': False, 'errors': 'Invalid request method'}, status=400)

    try:
        logger.error(f"POST data received for booking: {dict(request.POST)}")
        checkin = parse_date(request.POST.get('modalCheckin'))
        checkout = parse_date(request.POST.get('modalCheckout'))
        room_type_id = request.POST.get('roomType')
        guests = int(request.POST.get('modalGuests', 0))
        # Accept both modalRooms and rooms for robustness
        rooms = int(request.POST.get('modalRooms') or request.POST.get('rooms') or 0)
        base_price_str = request.POST.get('modalBasePrice', '0').replace('₦', '').strip()
        total_cost_str = request.POST.get('modalTotalCost', '0').replace('₦', '').strip()
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        special_requests = request.POST.get('special_requests', '')
        logger.error(f"transaction_id: {request.POST.get('transaction_id')}, payment_status: {request.POST.get('payment_status')}")

        required_fields = {
            'checkin': checkin, 'checkout': checkout, 'room_type': room_type_id,
            'guests': guests, 'rooms': rooms, 'first_name': first_name,
            'last_name': last_name, 'email': email, 'phone': phone
        }
        missing = [key for key, value in required_fields.items() if not value]
        if missing:
            logger.warning(f"Missing fields: {', '.join(missing)}")
            return JsonResponse({'success': False, 'errors': f"Missing fields: {', '.join(missing)}"}, status=400)

        if checkin >= checkout or checkin < date.today():
            logger.warning("Invalid check-in/check-out dates")
            return JsonResponse({'success': False, 'errors': 'Invalid check-in/check-out dates'}, status=400)
        if guests <= 0 or rooms <= 0:
            logger.warning("Guests and rooms must be positive")
            return JsonResponse({'success': False, 'errors': 'Guests and rooms must be positive'}, status=400)

        base_price = Decimal(base_price_str)
        total_cost = Decimal(total_cost_str)

        room_type = RoomType.objects.get(id=room_type_id)
        available_rooms = Room.objects.filter(
            room_type=room_type, is_available=True
        ).exclude(
            booking__checkin__lt=checkout,
            booking__checkout__gt=checkin,
            booking__status='confirmed'
        )
        if available_rooms.count() < rooms:
            logger.warning(f"Not enough rooms available: {rooms} requested, {available_rooms.count()} available")
            return JsonResponse({'success': False, 'errors': f'Only {available_rooms.count()} room(s) available'}, status=400)

        # Accept payment_status and transaction_id from POST (preferred over session)
        payment_status = request.POST.get('payment_status') or request.session.get('payment_status')
        transaction_id = request.POST.get('transaction_id') or request.session.get('transaction_id')
        expected_amount = request.session.get('expected_amount')
        if payment_status != 'success' or not transaction_id or not expected_amount:
            logger.warning("Booking attempted without successful payment")
            return JsonResponse({'success': False, 'errors': 'Payment not verified'}, status=400)

        # Create booking first
        booking = Booking(
            room=available_rooms.first(),
            checkin=checkin,
            checkout=checkout,
            guests=guests,
            total_price=total_cost,
            special_request=special_requests,
            status='confirmed',
            transaction_id=transaction_id
        )
        booking.save()

        # Create guest and associate with booking
        guest = Guest.objects.create(
            booking=booking,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone
        )

        logger.info(f"Booking created: ID {booking.id} for {guest.email}, transaction_id={transaction_id}")
        return JsonResponse({'success': True, 'booking_id': booking.id})

    except RoomType.DoesNotExist:
        logger.error("Invalid room type")
        return JsonResponse({'success': False, 'errors': 'Invalid room type'}, status=400)
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return JsonResponse({'success': False, 'errors': str(e)}, status=400)
    except ValueError as e:
        logger.error(f"Invalid numeric value: {str(e)}")
        return JsonResponse({'success': False, 'errors': f'Invalid numeric value: {str(e)}'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({'success': False, 'errors': f'Unexpected error: {str(e)}'}, status=400)

@require_POST
@csrf_exempt
def verify_payment(request):
    try:
        # Enhanced logging for debugging
        logger.error(f"=== VERIFY PAYMENT START ===")
        logger.error(f"Request method: {request.method}")
        logger.error(f"Request headers: {dict(request.headers)}")
        logger.error(f"Request content type: {request.content_type}")
        
        # Handle different request formats
        reference = None
        data = {}
        
        # Try to get data from request body first
        if hasattr(request, 'body') and request.body:
            try:
                raw_body = request.body.decode('utf-8')
                logger.error(f"Raw request body: {raw_body}")
                
                if raw_body.strip():
                    data = json.loads(raw_body)
                    reference = data.get('reference')
                    logger.error(f"Extracted reference from body: {reference}")
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                logger.error(f"Error parsing request body: {str(e)}")
        
        # Fallback to POST data if body parsing failed
        if not reference and request.POST:
            logger.error(f"Trying POST data: {dict(request.POST)}")
            reference = request.POST.get('reference')
            logger.error(f"Extracted reference from POST: {reference}")
        
        # Fallback to GET data if still no reference
        if not reference and request.GET:
            logger.error(f"Trying GET data: {dict(request.GET)}")
            reference = request.GET.get('reference')
            logger.error(f"Extracted reference from GET: {reference}")

        if not reference:
            logger.error("Missing reference in request data")
            logger.error(f"POST data: {dict(request.POST)}")
            logger.error(f"GET data: {dict(request.GET)}")
            logger.error(f"Body data: {data}")
            return JsonResponse({'status': 'error', 'message': 'Missing reference'}, status=400)

        # Check if Paystack secret key is configured
        if not hasattr(settings, 'PAYSTACK_SECRET_KEY') or not settings.PAYSTACK_SECRET_KEY:
            logger.error("PAYSTACK_SECRET_KEY not configured")
            return JsonResponse({'status': 'error', 'message': 'Payment system not configured'}, status=500)

        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        logger.error(f"Sending verification request to Paystack for reference: {reference}")
        
        try:
            response = requests.get(
                f'https://api.paystack.co/transaction/verify/{reference}',
                headers=headers,
                timeout=30
            )
        except requests.RequestException as e:
            logger.error(f"Network error verifying payment: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'Network error: {str(e)}'}, status=500)
        
        try:
            response_data = response.json()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Paystack: {response.text}")
            return JsonResponse({'status': 'error', 'message': 'Invalid response from payment provider'}, status=500)
        
        logger.error(f"Paystack response: status_code={response.status_code}, data={response_data}")

        if response.status_code == 200 and response_data.get('status') and response_data.get('data', {}).get('status') == 'success':
            expected_amount = request.session.get('expected_amount')
            logger.error(f"Session expected_amount: {expected_amount}")
            
            if not expected_amount:
                logger.error("No expected amount in session")
                return JsonResponse({'status': 'error', 'message': 'Session expired. Please try again.'}, status=400)
            
            expected_amount = Decimal(expected_amount)  # Already in Naira
            paid_amount = Decimal(response_data['data']['amount']) / 100  # Convert kobo to Naira
            logger.error(f"Comparing amounts: expected={expected_amount}, paid={paid_amount}, raw_paid_amount={response_data['data']['amount']}")

            if abs(paid_amount - expected_amount) > Decimal('0.01'):  # Allow small rounding differences
                logger.error(f"Amount mismatch: expected {expected_amount}, paid {paid_amount}")
                return JsonResponse({'status': 'error', 'message': f'Payment amount mismatch. Expected: ₦{expected_amount}, Paid: ₦{paid_amount}'}, status=400)

            request.session['payment_status'] = 'success'
            request.session['transaction_id'] = response_data['data']['id']
            request.session.modified = True
            logger.info(f"Payment verified: reference={reference}, transaction_id={response_data['data']['id']}")
            return JsonResponse({
                'status': 'success',
                'message': 'Payment verified',
                'transaction_id': response_data['data']['id'],
                'payment_status': 'success'
            })
        else:
            logger.error(f"Payment verification failed: reference={reference}, response: {response_data}")
            error_message = 'Payment verification failed'
            if response_data.get('message'):
                error_message = response_data['message']
            return JsonResponse({'status': 'failed', 'message': error_message}, status=400)

    except Exception as e:
        logger.error(f"Unexpected error verifying payment: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': f'Unexpected error: {str(e)}'}, status=500)

@require_POST
@csrf_exempt
def store_expected_amount(request):
    try:
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            amount = data.get('amount')
        else:
            amount = request.POST.get('amount')
            
        if not amount or float(amount) <= 0:
            logger.warning("Invalid amount provided")
            return JsonResponse({'success': False, 'errors': 'Invalid amount'}, status=400)
        request.session['expected_amount'] = str(amount)
        logger.info(f"Stored expected amount: {amount}")
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Error storing expected amount: {str(e)}")
        return JsonResponse({'success': False, 'errors': str(e)}, status=400)

@require_POST
@csrf_exempt
def webhook(request):
    try:
        payload = json.loads(request.body)
        event = payload.get('event')
        if event == 'charge.success':
            reference = payload['data']['reference']
            status = payload['data']['status']
            logger.info(f"Webhook received: event={event}, reference={reference}, status={status}")
            # Update booking status if needed
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JsonResponse({'status': 'error'}, status=400)