from __future__ import annotations
from enum import Enum

from ..helper.quality_of_life import classproperty

__all__ = [
    "Preprocessables",
    "Informables",
]


class Preprocessables(Enum):
    """ PreProcessType """
    # Swap
    SWAP = "Swap"                      # To determine if swap needs to cost more or less,
    #                                  # if swap is fast action or combat action...
    SWAP_COST_ANY = "SwapCostAny"      # Discount any dice cost for swap
    SWAP_COST_ELEM = "SwapCostElem"    # Discount dice cost for swap of specific element
    SWAP_COST_OMNI = "SwapCostOmni"    # Discount dice cost for swap of any element
    # Skill
    SKILL = "Skill"                    # same as SWAP but for skill
    SKILL_COST_ANY = "SkillCostAny"    # Discount any dice cost for skill
    SKILL_COST_ELEM = "SkillCostElem"  # Discount dice cost for skill of specific element
    SKILL_COST_OMNI = "SkillCostOmni"  # Discount dice cost for skill of any element
    # Card
    CARD1 = "Card1"                    # same as SWAP but for card, for the first time
    CARD2 = "Card2"                    # same as SWAP but for card, for the second time
    CARD1_COST_ANY = "Card1CostAny"    # Discount any dice cost for card1
    CARD2_COST_ANY = "Card2CostAny"    # Discount any dice cost for card2
    CARD1_COST_ELEM = "Card1CostElem"  # Discount dice cost for card1 of specific element
    CARD2_COST_ELEM = "Card2CostElem"  # Discount dice cost for card2 of specific element
    CARD1_COST_OMNI = "Card1CostOmni"  # Discount dice cost for card1 of any element
    CARD2_COST_OMNI = "Card2CostOmni"  # Discount dice cost for card2 of any element
    # Damages
    DMG_ELEMENT = "DmgElement"         # To determine the element
    DMG_REACTION = "DmgReaction"       # To determine the reaction
    DMG_AMOUNT_PLUS = "DmgNumberPlus"  # To determine final amount of damage (addition/subtraction)
    DMG_AMOUNT_MINUS = "DmgNumberMinus"# To determine final amount of damage (addition/subtraction)
    DMG_AMOUNT_MUL = "DmgNumberMul"    # To determine final amount of damage (multiplication/division)
    # Roll Phase
    ROLL_CHANCES = "RollChances"       # To modify the roll chances
    ROLL_DICE_INIT = "RollDiceInit"    # To modify the initial dice

    @classproperty
    def swap_order(cls) -> tuple[Preprocessables, ...]:
        return cls.SWAP_COST_ANY, cls.SWAP_COST_ELEM, cls.SWAP_COST_OMNI, cls.SWAP  # type: ignore

    @classproperty
    def skill_order(cls) -> tuple[Preprocessables, ...]:
        return cls.SKILL_COST_ANY, cls.SKILL_COST_ELEM, cls.SKILL_COST_OMNI, cls.SKILL  # type: ignore
    
    @classproperty
    def card_order(cls) -> tuple[Preprocessables, ...]:
        return (  # type: ignore
            cls.CARD1_COST_ANY, cls.CARD1_COST_ELEM, cls.CARD1_COST_OMNI,
            cls.CARD2_COST_ANY, cls.CARD2_COST_ELEM, cls.CARD2_COST_OMNI,
            cls.CARD1, cls.CARD2,
        )

class Informables(Enum):
    DMG_DEALT = "DmgDealt"
    HEALING = "Healing"
    REACTION_TRIGGERED = "ReactionTriggered"
    PRE_SKILL_USAGE = "PreSkillUsage"
    POST_SKILL_USAGE = "PostSkillUsage"
    CHARACTER_DEATH = "CharacterDeath"
    EQUIPMENT_DISCARDING = "EquipmentDiscarding"

    # removals
    SUPPORT_REMOVAL = "SupportRemoval"
