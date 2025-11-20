# myapp/templatetags/dict_filters.py
from django import template
import re

register = template.Library()
PARTY_LEVEL = 5
level_msgs = {
    "lte" : "This creature can't off-guard Valyas via flanking, hidden, undetected or using Surprise Attack"
}
traits_msgs = {
    "fear" : "Bors gets a critical success on a success if it's a Will ST, and reduces the initial Frightened condition by 1"
}

@register.filter
def level_offset(template_type, level):
    """
    Returns the offset depending on the level and template.
    """
    level = int(level)
    if template_type == "weak":
        return -1 if level > 1 else -2
    elif template_type == "elite":
        return 1 if level > 1 else 2
    return 0
@register.filter
def hp_offset(template_type, level):
    """
    Returns the offset depending on the level and template.
    """
    level = int(level)
    if template_type == "weak":
        if 0<level<3 :
            return -10
        elif 2<level<6 :
            return -15
        elif 5<level<21 :
            return -20
        elif 20<level :
            return -30
    elif template_type == "elite":
        if level<2 :
            return 10
        elif 1<level<5 :
            return 15
        elif 4<level<20 :
            return 20
        elif 19<level :
            return 30
    return 0
@register.filter
def skill_offset(template_type, level):
    """
    Returns the offset depending on the level and template.
    """
    if template_type == "weak":
        return -2
    elif template_type == "elite":
        return +2
    return 0

@register.filter(name="replace_dash")
def replace_dash(value: str) -> str:
    """Replace - with ' '."""
    return value.replace("-", " ")

@register.filter
def replace_actions(actions: str) -> str:
    """
    Replace numeric action markers in a string with PF2e symbols.
    """
    mapping = {
        "-1": "⟳",
        "1": "◆",
        "2": "◆◆",
        "3": "◆◆◆",
        "0": "◇",
    }
    actions_str = str(actions)
    if actions is not None and not ("round" in actions_str or "minute" in actions_str):
        for key, symbol in mapping.items():
            actions_str = actions_str.replace(key, symbol)
        return actions_str
    return actions or "Passive"

@register.filter
def level_interactions(level):
    level = int(level)
    msg = ''
    if level <= PARTY_LEVEL:
        msg+= "<p class='warning'>"+level_msgs["lte"]+"</p>"
    return msg

@register.filter
def trait_interactions(traits):
    msg = ''
    for trait in traits:
        if trait in traits_msgs:
            msg+= "<p class='warning'>"+traits_msgs[trait]+"</p>"
    return msg

@register.filter
def calculate_damage(damage_roll, offset):
    if damage_roll is None:
        return ""
    try:
        offset = int(offset)
    except (TypeError, ValueError):
        return damage_roll 
    damage_roll = damage_roll.replace(" ","")
    match = re.match(r'^(\d+d\d+)([+-]\d+)?$', damage_roll.strip())
    if not match:
        return f"{damage_roll} {offset:+d}"
    dice = match.group(1)
    modifier_str = match.group(2)
    if modifier_str:
        current_mod = int(modifier_str)
    else:
        current_mod = 0

    new_mod = current_mod + offset
    if new_mod == 0:
        return dice
    return f"{dice}{new_mod:+d}"