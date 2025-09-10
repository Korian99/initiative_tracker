# myapp/templatetags/dict_filters.py
from django import template

register = template.Library()

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
    if actions and not ("round" in actions_str or "minute" in actions_str):
        for key, symbol in mapping.items():
            actions = actions_str.replace(key, symbol)
    return actions or "Passive or ◇"
