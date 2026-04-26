"""LLM-powered message generation for negotiations."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

INTRO_MESSAGE_TEMPLATE = """You are a buyer negotiating the purchase of {product}.
Your goal is to close at or below {target_price} AED.
Your absolute maximum is {max_price} AED.
The seller's name is {seller_name}.
Current strategy: {strategy}.
You are starting the negotiation.

Generate a short, natural first message to send to the seller:
- Introduce yourself as a buyer
- Express interest in the item
- Ask one qualifying question (condition, location, etc.)
- Do NOT mention price yet
- 2-3 sentences maximum
- Sound friendly and genuine

Message:"""

COUNTER_OFFER_TEMPLATE = """You are negotiating the purchase of {product}.
Current list price: {list_price} AED
Your target: {target_price} AED
Your max: {max_price} AED
Your current offer: {current_offer} AED
Seller's last price: {seller_price} AED
Strategy: {strategy}
Round {round}/{max_rounds}

Context from conversation:
{conversation}

Generate a counter-offer message:
- Acknowledge the seller's position
- Present your counter-offer of {counter_offer} AED
- Provide a reasonable justification
- Be polite but firm
- 2-4 sentences maximum

Message:"""

ACCEPT_MESSAGE_TEMPLATE = """You are accepting a seller's offer.
Item: {product}
Agreed price: {agreed_price} AED
Seller: {seller_name}

Generate a brief acceptance message:
- Confirm you accept the price
- Ask about pickup/delivery
- Express enthusiasm
- 1-2 sentences

Message:"""

REJECT_MESSAGE_TEMPLATE = """You are ending the negotiation because the price is too high.
Item: {product}
Your max: {max_price} AED
Seller's price: {seller_price} AED
Seller: {seller_name}

Generate a polite exit message:
- Thank the seller for their time
- Explain the price is above budget
- Leave door open for future
- 1-2 sentences

Message:"""


async def generate_message(
    prompt: str,
    model: str = "gpt-4o",
) -> str:
    try:
        from litellm import acompletion
        response = await acompletion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return ""


async def generate_intro_message(
    product: str,
    seller_name: str,
    target_price: float,
    max_price: float,
    strategy: str,
) -> str:
    prompt = INTRO_MESSAGE_TEMPLATE.format(
        product=product,
        seller_name=seller_name,
        target_price=target_price,
        max_price=max_price,
        strategy=strategy,
    )
    return await generate_message(prompt)


async def generate_counter_message(
    product: str,
    list_price: float,
    target_price: float,
    max_price: float,
    current_offer: float,
    seller_price: float,
    strategy: str,
    round_num: int,
    max_rounds: int,
    conversation: str = "",
) -> str:
    prompt = COUNTER_OFFER_TEMPLATE.format(
        product=product,
        list_price=list_price,
        target_price=target_price,
        max_price=max_price,
        current_offer=current_offer,
        seller_price=seller_price,
        strategy=strategy,
        round=round_num,
        max_rounds=max_rounds,
        conversation=conversation,
    )
    return await generate_message(prompt)


async def generate_accept_message(
    product: str,
    agreed_price: float,
    seller_name: str,
) -> str:
    prompt = ACCEPT_MESSAGE_TEMPLATE.format(
        product=product,
        agreed_price=agreed_price,
        seller_name=seller_name,
    )
    return await generate_message(prompt)


async def generate_reject_message(
    product: str,
    max_price: float,
    seller_price: float,
    seller_name: str,
) -> str:
    prompt = REJECT_MESSAGE_TEMPLATE.format(
        product=product,
        max_price=max_price,
        seller_price=seller_price,
        seller_name=seller_name,
    )
    return await generate_message(prompt)