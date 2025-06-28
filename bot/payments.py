"""
Payment handling for LucoSMS integration using a conversational flow.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from bot.api_client import LucoSMSClient

logger = logging.getLogger(__name__)
client = LucoSMSClient()

# Conversation states
EMAIL, AMOUNT, CONFIRMATION = range(3)

# Preset amounts for quick selection
PRESET_AMOUNTS = [5000, 10000, 25000, 50000, 100000]

async def start_recharge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the recharge conversation by asking for an email."""
    user = update.effective_user
    context.user_data['recharge_info'] = {
        'telegram_id': user.id,
        'name': user.full_name
    }
    
    await update.message.reply_text(
        f"Hi {user.first_name}! Let's top up your account.\n\n"
        "Please enter your email address to continue."
    )
    return EMAIL

async def ask_for_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the email and asks for the amount."""
    email = update.message.text
    if '@' not in email or '.' not in email:
        await update.message.reply_text("That doesn't look like a valid email. Please try again.")
        return EMAIL
        
    context.user_data['recharge_info']['email'] = email
    
    buttons = [
        InlineKeyboardButton(f"UGX {amt:,}", callback_data=f"recharge_{amt}") 
        for amt in PRESET_AMOUNTS
    ]
    keyboard = [buttons[i:i + 3] for i in range(0, len(buttons), 3)]

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Great! Now, please select a top-up amount or enter a custom amount in UGX:",
        reply_markup=reply_markup
    )
    return AMOUNT

async def generate_payment_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the amount and generates the payment link."""
    amount = 0
    query = update.callback_query
    message_to_edit = None

    if query:
        await query.answer()
        amount = int(query.data.split('_')[1])
        message_to_edit = await query.edit_message_text(f"Processing UGX {amount:,}...")
    else:
        try:
            amount = float(update.message.text)
            if amount <= 0:
                await update.message.reply_text("Please enter a positive amount.")
                return AMOUNT
        except ValueError:
            await update.message.reply_text("That's not a valid number. Please enter a numeric amount.")
            return AMOUNT
        message_to_edit = await update.message.reply_text(f"Processing UGX {amount:,}...")

    context.user_data['recharge_info']['amount'] = amount
    info = context.user_data['recharge_info']
    
    processing_message = query.message if query else await update.message.reply_text("Generating your secure payment link...")

    try:
        payment_data = await client.initiate_payment(
            name=info['name'],
            email=info['email'],
            amount=info['amount'],
            telegram_id=str(info['telegram_id'])
        )

        if payment_data and payment_data.get('redirect_url'):
            redirect_url = payment_data['redirect_url']
            order_tracking_id = payment_data.get('order_tracking_id')
            
            if not order_tracking_id:
                await processing_message.edit_text("Payment initiation failed: Missing Order Tracking ID. Please contact support.")
                return ConversationHandler.END

            context.user_data['recharge_info']['order_tracking_id'] = order_tracking_id

            keyboard = [
                [InlineKeyboardButton("Click here to Pay", url=redirect_url)],
                [InlineKeyboardButton("✅ I have paid", callback_data=f"verify_{order_tracking_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await processing_message.edit_text(
                "Your payment link is ready. Please click the button below to complete the payment. "
                "Once you're done, come back and click 'I have paid'.",
                reply_markup=reply_markup
            )
            return CONFIRMATION
        else:
            error_message = payment_data.get('message', 'could not create a payment link')
            await processing_message.edit_text(f"Sorry, we {error_message}. Please try again later.")
            return ConversationHandler.END

    except Exception as e:
        logger.error(f"Error initiating payment: {e}")
        await processing_message.edit_text("An unexpected error occurred. Please contact support.")
        return ConversationHandler.END

async def verify_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Verifies the payment status after the user confirms."""
    query = update.callback_query
    await query.answer()
    
    order_tracking_id = query.data.split('_')[1]
    
    await query.edit_message_text("Verifying your payment, please wait...")

    try:
        payment_status = await client.get_payment_status(order_tracking_id)
        
        if not payment_status:
            await query.edit_message_text("Could not retrieve payment status. Please try again in a moment or contact support.")
            return ConversationHandler.END

        is_success = payment_status.get("status") == "success" and \
                     payment_status.get("payment_status_description", "").lower() == "completed"

        if is_success:
            paid_amount = float(payment_status.get("amount", 0))
            original_amount = float(context.user_data.get('recharge_info', {}).get('amount', -1))

            # Validate that the paid amount matches the original amount
            if paid_amount != original_amount:
                logger.warning(
                    f"Payment amount mismatch for OrderTrackingId {order_tracking_id}. "
                    f"Expected {original_amount}, but paid {paid_amount}."
                )
                await query.edit_message_text(
                    "There was a mismatch in the payment amount. "
                    "Please contact support for assistance."
                )
                return ConversationHandler.END

            user_id = str(context.user_data['recharge_info']['telegram_id'])
            
            await query.edit_message_text("Payment successful! Updating your wallet...")
            
            topup_result = await client.topup_wallet(user_id, paid_amount)

            if topup_result and topup_result.get('success'):
                new_balance = topup_result.get('new_balance', 'N/A')
                receipt_text = (
                    f"✅ **Top-up Successful!**\n\n"
                    f"Your wallet has been credited with **UGX {paid_amount:,.0f}**.\n"
                    f"Your new balance is: **{new_balance}**.\n\n"
                    "Thank you for your recharge!"
                )
                await query.edit_message_text(receipt_text, parse_mode='Markdown')
            else:
                error_msg = topup_result.get('error', 'an unknown error') if topup_result else 'an unknown error'
                await query.edit_message_text(f"Your payment was successful, but we failed to top up your wallet. Please contact support. Error: {error_msg}")
        else:
            status_desc = payment_status.get("payment_status_description", "not completed")
            await query.edit_message_text(f"Your payment could not be confirmed (Status: {status_desc}). If you have paid, please try again in a few moments or contact support.")

    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        await query.edit_message_text("An error occurred while verifying your payment. Please contact support.")
        
    context.user_data.pop('recharge_info', None)
    return ConversationHandler.END

async def cancel_recharge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the recharge conversation."""
    message = update.message or update.callback_query.message
    await message.reply_text("Recharge process cancelled.")
    context.user_data.pop('recharge_info', None)
    return ConversationHandler.END
