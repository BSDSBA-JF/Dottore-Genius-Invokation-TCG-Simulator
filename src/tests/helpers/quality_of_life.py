from __future__ import annotations
from dataclasses import dataclass, replace
from typing import ClassVar, cast, Iterable

from typing_extensions import Self

from src.dgisim.action.action import *
from src.dgisim.agents import *
from src.dgisim.card.card import Card
from src.dgisim.card.cards import Cards, OrderedCards
from src.dgisim.character.character import Character
from src.dgisim.character.characters import Characters
from src.dgisim.character.enums import CharacterSkill
from src.dgisim.deck import Deck
from src.dgisim.dice import ActualDice
from src.dgisim.effect.effect import *
from src.dgisim.effect.enums import DynamicCharacterTarget, TriggeringSignal, Zone
from src.dgisim.effect.structs import DamageType, StaticTarget
from src.dgisim.element import *
from src.dgisim.event import *
from src.dgisim.game_state_machine import GameStateMachine
from src.dgisim.helper.level_print import GamePrinter
from src.dgisim.helper.quality_of_life import *
from src.dgisim.phase import Phase
from src.dgisim.state.enums import Pid
from src.dgisim.state.game_state import GameState
from src.dgisim.state.player_state import PlayerState
from src.dgisim.status.enums import *
from src.dgisim.status.status import *


@dataclass(frozen=True, kw_only=True)
class _TempTestDmgListenerStatus(PlayerHiddenStatus):
    dmgs: tuple[SpecificDamageEffect, ...] = ()

    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.DMG_DEALT:
            assert isinstance(information, DmgIEvent)
            if information.dmg.source.pid is status_source.pid:
                return replace(self, dmgs=self.dmgs + (information.dmg,))
        return self

    def __str__(self) -> str:
        return super().__str__() + f"({len(self.dmgs)})"


@dataclass(frozen=True, kw_only=True)
class _TempTestInfiniteRevivalStatus(CharacterHiddenStatus, RevivalStatus):
    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.TRIGGER_REVIVAL,
    })

    def revivable(
            self, game_state: GameState, status_source: StaticTarget, char_source: StaticTarget,
    ) -> bool:
        return status_source == char_source

    def _post_update_react_to_signal(
            self,
            game_state: GameState,
            effects: list[Effect],
            source: StaticTarget,
            signal: TriggeringSignal,
            detail: None | InformableEvent,
    ) -> list[Effect]:
        if signal is TriggeringSignal.TRIGGER_REVIVAL:
            effects.append(
                ReviveRecoverHPEffect(
                    source=source,
                    target=source,
                    recovery=BIG_INT,
                ),
            )
        return effects


@dataclass(frozen=True, kw_only=True)
class _TempTestDmgStatus(CharacterStatus):
    dmg: int
    elem: Element
    target: StaticTarget
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
    ))

    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL:
            return [
                SpecificDamageEffect(
                    source=source,
                    target=source,
                    element=self.elem,
                    damage=self.dmg,
                    damage_type=DamageType(status=True, no_boost=True),
                ),
            ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class _TempTestHealingStatus(CharacterStatus):
    healing: int
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
    ))

    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL:
            return [
                RecoverHPEffect(
                    source=source,
                    target=source,
                    recovery=self.healing,
                ),
            ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class _TempTestThickShieldStatus(CharacterStatus, StackedShieldStatus):
    """
    can take BIG_INT to BIG_INT^2 non-PIERCING damage
    """
    usages: int = BIG_INT
    MAX_USAGES: ClassVar[int] = BIG_INT
    SHIELD_AMOUNT: ClassVar[int] = BIG_INT


def add_damage_effect(
        game_state: GameState,
        damage: int,
        elem: Element,
        pid: Pid = Pid.P2,
        char_id: None | int = None,
        damage_type: None | DamageType = None,
) -> GameState:
    """
    Adds ReferredDamageEffect to Player2's active character with `damage` and `elem` from Player1's
    active character (id=1)
    """
    return game_state.factory().f_effect_stack(
        lambda es: es.push_many_fl((
            ReferredDamageEffect(
                source=StaticTarget(
                    pid.other,
                    Zone.CHARACTERS,
                    case_val(char_id is None, 1, char_id),  # type: ignore
                ),
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=elem,
                damage=damage,
                damage_type=case_val(damage_type is None, DamageType(),
                                     damage_type),  # type: ignore
            ),
            AliveMarkCheckerEffect(),
            DefeatedMarkCheckerEffect(),
            DeathCheckCheckerEffect(),
        ))
    ).build()


def add_dmg_listener(game_state: GameState, pid: Pid) -> GameState:
    """
    :param pid: the player that will receive the damage
    """
    return AddHiddenStatusEffect(
        pid,
        status=_TempTestDmgListenerStatus,
    ).execute(game_state)


def apply_elemental_aura(
        game_state: GameState,
        element: Element,
        pid: Pid,
        char_id: None | int = None,
) -> GameState:
    """
    Apply elemental aura to the target character.
    If char_id is None (by default), then active character of pid is targeted.
    """
    if char_id is None:
        target = StaticTarget.from_player_active(game_state, pid)
    else:
        target = StaticTarget.from_char_id(pid, char_id)
    return auto_step(
        ApplyElementalAuraEffect(
            source=target,
            target=target,
            element=element,
            source_type=DamageType(status=True),
        ).execute(game_state)
    )


def auto_step(game_state: GameState, observe: bool = False) -> GameState:
    """ Step the game state until a player action is required. """
    gsm = GameStateMachine(game_state, PuppetAgent(), PuppetAgent())
    if not observe:
        gsm.auto_step()
    else:  # pragma: no cover
        while gsm.get_game_state().waiting_for() is None:
            gsm.one_step()
            print(GamePrinter.dict_game_printer(gsm.get_game_state().dict_str()))
            input(":> ")
    return gsm.get_game_state()


def recharge_energy_for_all(game_state: GameState) -> GameState:
    return game_state.factory().f_player1(
        lambda p1: p1.factory().f_characters(
            lambda cs: cs.factory().f_characters(
                lambda chars: tuple(
                    char.factory().energy(char.max_energy).build()
                    for char in chars
                )
            ).build()
        ).build()
    ).f_player2(
        lambda p2: p2.factory().f_characters(
            lambda cs: cs.factory().f_characters(
                lambda chars: tuple(
                    char.factory().energy(char.max_energy).build()
                    for char in chars
                )
            ).build()
        ).build()
    ).build()


def drain_energy_for_all(game_state: GameState) -> GameState:
    return game_state.factory().f_player1(
        lambda p1: p1.factory().f_characters(
            lambda cs: cs.factory().f_characters(
                lambda chars: tuple(
                    char.factory().energy(0).build()
                    for char in chars
                )
            ).build()
        ).build()
    ).f_player2(
        lambda p2: p2.factory().f_characters(
            lambda cs: cs.factory().f_characters(
                lambda chars: tuple(
                    char.factory().energy(0).build()
                    for char in chars
                )
            ).build()
        ).build()
    ).build()


def fill_dice_with_omni(game_state: GameState) -> GameState:
    dice = {
        Element.OMNI: BIG_INT,
        Element.PYRO: BIG_INT,
        Element.HYDRO: BIG_INT,
        Element.ANEMO: BIG_INT,
        Element.ELECTRO: BIG_INT,
        Element.DENDRO: BIG_INT,
        Element.CRYO: BIG_INT,
        Element.GEO: BIG_INT,
    }
    return game_state.factory().f_player1(
        lambda p: p.factory().dice(ActualDice(dice)).build()
    ).f_player2(
        lambda p: p.factory().dice(ActualDice(dice)).build()
    ).build()


def full_action_step(game_state: GameState, observe: bool = False) -> GameState:
    gsm = GameStateMachine(game_state, PuppetAgent(), PuppetAgent())
    gsm.player_step(observe=observe)
    gsm.auto_step(observe=observe)
    return gsm.get_game_state()


def get_dmg_listener_data(game_state: GameState, pid: Pid) -> tuple[SpecificDamageEffect, ...]:
    hidden_statuses = game_state.get_player(pid).hidden_statuses
    assert _TempTestDmgListenerStatus in hidden_statuses
    listener = hidden_statuses.just_find(_TempTestDmgListenerStatus)
    return listener.dmgs


def grant_all_infinite_revival(game_state: GameState) -> GameState:
    """
    Gives all alive characters a hidden character revival status,
    that can revive the attached character infinite times.
    """
    for pid in (Pid.P1, Pid.P2):
        alive_chars = game_state.get_player(pid).characters.get_alive_characters()
        for char in alive_chars:
            game_state = AddCharacterStatusEffect(
                target=StaticTarget.from_char_id(pid, char.id),
                status=_TempTestInfiniteRevivalStatus,
            ).execute(game_state)
    return game_state


def grant_all_thick_shield(game_state: GameState) -> GameState:
    """
    Gives all alive characters a character status of StackedShield,
    that can be assumed to abosrb all reasonable damages in the entire game.
    (except PIERCING damage of course)
    """
    for pid in (Pid.P1, Pid.P2):
        alive_chars = game_state.get_player(pid).characters.get_alive_characters()
        for char in alive_chars:
            game_state = AddCharacterStatusEffect(
                target=StaticTarget.from_char_id(pid, char.id),
                status=_TempTestThickShieldStatus,
            ).execute(game_state)
    return game_state


def heal_for_all(game_state: GameState) -> GameState:
    """ only heals the alive characters """
    def heal_player(player: PlayerState) -> PlayerState:
        return player.factory().f_characters(
            lambda cs: cs.factory().f_characters(
                lambda chars: tuple(
                    char.factory().hp(char.max_hp if char.is_alive() else 0).build()
                    for char in chars
                )
            ).build()
        ).build()

    return game_state.factory().f_player1(heal_player).f_player2(heal_player).build()


def kill_character(
        game_state: GameState,
        char_id: int,
        pid: Pid = Pid.P2,
        hp: int = 0,
) -> GameState:
    """
    Sets Player2's active character's hp to `hp` (default=0)
    """
    return game_state.factory().f_player(
        pid,
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().f_character(
                char_id,
                lambda c: c.factory().hp(hp).alive(hp > 0).build()
            ).build()
        ).build()
    ).build()


def set_hp(
        game_state: GameState, pid: Pid, hp: int,
        char_id: None | int = None, revive: bool = False, observe: bool = False,
) -> GameState:
    """
    :param hp: should be greater than 0, because this function is not for killing characters.

    It is not advised to revive characters with this function.
    As revival will be treated as healing, and may cause further effects.
    """
    assert hp > 0
    cs = game_state.get_player(pid).characters
    if char_id is not None:
        c = cs.just_get_character(char_id)
        if c.is_defeated():
            return auto_step(ReviveRecoverHPEffect(
                StaticTarget.from_char_id(pid, char_id),
                StaticTarget.from_char_id(pid, char_id),
                recovery=hp,
            ).execute(game_state), observe=True)
        return game_state.factory().f_player(
            pid,
            lambda p: p.factory().characters(
                cs.factory().f_character(
                    char_id,  # type: ignore
                    lambda c: c.factory().hp(min(hp, c.max_hp)).alive(hp > 0).build()
                ).build()
            ).build()
        ).build()

    game_state = game_state.factory().f_player(
        pid,
        lambda p: p.factory().characters(
            cs.factory().f_characters(
                lambda chars: tuple([
                    char.factory().hp(
                        min(hp, char.max_hp) if char.alive else 0
                    ).build()
                    for char in chars
                ])
            ).build()
        ).build()
    ).build()
    for char in cs:
        if char.is_defeated():
            game_state = auto_step(ReviveRecoverHPEffect(
                StaticTarget.from_char_id(pid, char.id),
                StaticTarget.from_char_id(pid, char.id),
                recovery=hp,
            ).execute(game_state), observe=observe)
    return game_state


def next_round(game_state: GameState, observe: bool = False) -> GameState:
    gsm = GameStateMachine(game_state, LazyAgent(), LazyAgent())
    gsm.step_until_phase(game_state.mode.end_phase, observe=observe)
    gsm.step_until_phase(game_state.mode.action_phase, observe=observe)
    gsm.auto_step(observe=observe)
    return gsm.get_game_state()


def next_round_with_great_omni(game_state: GameState, observe: bool = False) -> GameState:
    """ skips to next round and fill players with even number of dice """
    game_state = next_round(game_state, observe)
    return fill_dice_with_omni(game_state)


def oppo_aura_elem(game_state: GameState, elem: Element, char_id: None | int = None) -> GameState:
    """
    DEPRECATED, don't use for further tests.

    Gives Player2's active character `elem` aura
    """
    if char_id is None:
        return game_state.factory().f_player2(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_active_character(
                    lambda ac: ac.factory().elemental_aura(
                        ElementalAura.from_default().add(elem)
                    ).build()
                ).build()
            ).build()
        ).build()
    else:
        return game_state.factory().f_player2(
            lambda p: p.factory().f_characters(
                lambda cs: cs.factory().f_character(
                    char_id,  # type: ignore
                    lambda ac: ac.factory().elemental_aura(
                        ElementalAura.from_default().add(elem)
                    ).build()
                ).build()
            ).build()
        ).build()


def remove_all_infinite_revival(game_state: GameState) -> GameState:
    """
    Removes the infinite revival statuses granted.
    """
    for pid in (Pid.P1, Pid.P2):
        alive_chars = game_state.get_player(pid).characters.get_alive_characters()
        for char in alive_chars:
            game_state = RemoveCharacterStatusEffect(
                target=StaticTarget.from_char_id(pid, char.id),
                status=_TempTestInfiniteRevivalStatus,
            ).execute(game_state)
    return game_state


def remove_all_thick_shield(game_state: GameState) -> GameState:
    """
    Removes the thick shields generated by grant_all_thick_shield()
    """
    for pid in (Pid.P1, Pid.P2):
        alive_chars = game_state.get_player(pid).characters.get_alive_characters()
        for char in alive_chars:
            game_state = RemoveCharacterStatusEffect(
                target=StaticTarget.from_char_id(pid, char.id),
                status=_TempTestThickShieldStatus,
            ).execute(game_state)
    return game_state


def remove_aura(game_state: GameState, pid: Pid = Pid.P2, char_id: None | int = None) -> GameState:
    """ Removes all elemental aura of the target character, default to the active character. """
    return game_state.factory().f_player(
        pid,
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().f_character(
                case_val(char_id is None, cs.just_get_active_character_id(), char_id),  # type: ignore
                lambda c: c.factory().elemental_aura(ElementalAura.from_default()).build()
            ).build()
        ).build()
    ).build()


def remove_dmg_listener(game_state: GameState, pid: Pid) -> GameState:
    return RemoveHiddenStatusEffect(
        pid,
        status=_TempTestDmgListenerStatus,
    ).execute(game_state)


def replace_hand_cards(game_state: GameState, pid: Pid, cards: Cards) -> GameState:
    return game_state.factory().f_player(
        pid,
        lambda p: p.factory().hand_cards(cards).build()
    ).build()


def replace_deck_cards(game_state: GameState, pid: Pid, cards: Cards | OrderedCards) -> GameState:
    if isinstance(cards, Cards):
        cards = cards.to_ordered_cards()
    return game_state.factory().f_player(
        pid,
        lambda p: p.factory().deck_cards(cards).build()  # type: ignore
    ).build()

def replace_init_deck(game_state: GameState, pid: Pid, cards: Cards) -> GameState:
    new_deck: Deck = game_state.get_player(pid).initial_deck.to_mutable()
    new_deck.cards = cards.to_dict()
    new_deck = new_deck.to_frozen()
    return game_state.factory().f_player(
        pid,
        lambda p: p.factory().initial_deck(new_deck).build()
    ).build()

def replace_entire_deck(game_state: GameState, pid: Pid, cards: Cards | OrderedCards) -> GameState:
    """ Changes both init deck and runtime deck. """
    if isinstance(cards, Cards):
        cards = cards.to_ordered_cards()
    new_deck: Deck = game_state.get_player(pid).initial_deck.to_mutable()
    new_deck.cards = cards.to_dict()
    new_deck = new_deck.to_frozen()
    return game_state.factory().f_player(
        pid,
        lambda p: p.factory().deck_cards(cards).initial_deck(new_deck).build()  # type: ignore
    ).build()

def replace_character(
        game_state: GameState,
        pid: Pid,
        char: type[Character],
        char_id: int,
) -> GameState:
    # character_instance = char.from_default(char_id).factory().hp(char).alive(False).build()
    character_instance = char.from_default(char_id)
    game_state = game_state.factory().f_player(
        pid,
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().character(
                character_instance
            ).build()
        ).build()
    ).build()
    game_state = game_state.factory().f_effect_stack(
        lambda es: es.push_many_fl((
            PersonalStatusTriggererEffect(
                target=StaticTarget.from_char_id(pid, char_id),
                signal=TriggeringSignal.INIT_GAME_START,
            ),
            EffectsGroupEndEffect(),
        ))
    ).build()
    return auto_step(game_state)


def replace_character_make_active_add_card(
        game_state: GameState,
        pid: Pid,
        char: type[Character],
        char_id: int,
        card: type[Card],
) -> GameState:
    return replace_character(game_state, pid, char, char_id).factory().f_player(
        pid,
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(
                char_id
            ).build()
        ).f_hand_cards(
            lambda hcs: hcs.add(card).add(card)
        ).build()
    ).build()


def replace_dice(game_state: GameState, pid: Pid, dice: ActualDice) -> GameState:
    return game_state.factory().f_player(
        pid,
        lambda p: p.factory().dice(dice).build()
    ).build()


def set_active_player_id(game_state: GameState, pid: Pid, character_id: int) -> GameState:
    return game_state.factory().f_player(
        pid,
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(character_id).build()
        ).build()
    ).build()


def silent_fast_swap(game_state: GameState, pid: Pid, char_id: int) -> GameState:
    return game_state.factory().f_player(
        pid,
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().active_character_id(char_id).build()
        ).build()
    ).build()


def simulate_status_dmg(
        game_state: GameState, dmg_amount: int,
        element: Element = Element.PIERCING,
        pid: Pid = Pid.P2,
        char_id: None | int = None,
        observe: bool = False,
) -> GameState:
    """
    Simulate a damage from a test-only, one-time status that is on the target character.
    The damage is of type "no_boost".
    """
    target = (
        StaticTarget.from_player_active(game_state, pid)
        if char_id is None
        else StaticTarget.from_char_id(pid, char_id)
    )
    game_state = UpdateCharacterStatusEffect(
        target=target,
        status=_TempTestDmgStatus(
            dmg=dmg_amount,
            elem=element,
            target=target,
        ),
    ).execute(game_state)
    game_state = game_state.factory().f_effect_stack(
        lambda es: es.push_one(TriggerStatusEffect(
            target=target,
            status=_TempTestDmgStatus,
            signal=TriggeringSignal.POST_SKILL,
        ))
    ).build()
    return auto_step(game_state, observe=observe)


def simulate_status_heal(
        game_state: GameState, healing: int, pid: Pid,
        char_id: None | int = None,
        observe: bool = False,
):
    """
    Simulate a healing from a test-only, one-time status that is on the target character.
    """
    target = (
        StaticTarget.from_player_active(game_state, pid)
        if char_id is None
        else StaticTarget.from_char_id(pid, char_id)
    )
    game_state = UpdateCharacterStatusEffect(
        target=target,
        status=_TempTestHealingStatus(healing=healing),
    ).execute(game_state)
    game_state = game_state.factory().f_effect_stack(
        lambda es: es.push_one(TriggerStatusEffect(
            target=target,
            status=_TempTestHealingStatus,
            signal=TriggeringSignal.POST_SKILL,
        ))
    ).build()
    return auto_step(game_state, observe=observe)


def skip_action_round(game_state: GameState, pid: Pid) -> GameState:
    """ pid is the player that is skipped """
    assert pid is game_state.waiting_for()
    return auto_step(TurnEndEffect().execute(game_state))


def skip_action_round_until(game_state: GameState, pid: Pid) -> GameState:
    """ pid is the player that is skipped until. """
    count = 0
    while pid is not game_state.waiting_for():
        game_state = skip_action_round(game_state, just(game_state.waiting_for()))
        count += 1
        if count > 20:
            raise Exception(f"It seems {pid} has ended causing infinite loop in {game_state}")
    return game_state


def step_action(
        game_state: GameState,
        pid: Pid,
        player_action: PlayerAction,
        observe: bool = False
) -> GameState:
    game_state = just(game_state.action_step(pid, player_action))
    return auto_step(game_state, observe=observe)


def step_skill(
        game_state: GameState,
        pid: Pid,
        skill: CharacterSkill,
        dice: None | ActualDice = None,
        observe: bool = False,
) -> GameState:
    active_character = game_state.get_player(pid).just_get_active_character()
    if dice is None:
        dice_used = ActualDice({Element.OMNI: active_character.skill_cost(skill).num_dice()})
    else:
        dice_used = dice
    player_action = SkillAction(
        skill=skill,
        instruction=DiceOnlyInstruction(dice=dice_used)
    )
    return step_action(game_state, pid, player_action, observe=observe)


def step_swap(
        game_state: GameState,
        pid: Pid,
        char_id: int,
        cost: int = 1,
        observe: bool = False,
) -> GameState:
    player_action = SwapAction(
        char_id=char_id,
        instruction=DiceOnlyInstruction(
            dice=ActualDice({Element.OMNI: cost})
        )
    )
    return step_action(game_state, pid, player_action, observe=observe)


def step_until_phase(game_state: GameState, phase: type[Phase], observe: bool = False) -> GameState:
    """ If game state is already in the `phase` then skip until the next one. """
    gsm = GameStateMachine(game_state, LazyAgent(), LazyAgent())
    gsm.step_until_phase(phase, observe=observe)
    return gsm.get_game_state()


def step_until_signal(game_state: GameState, signal: TriggeringSignal, observe: bool = False) -> GameState:
    """ Step until the next effect is trigger all statuses with `signal` """
    gsm = GameStateMachine(game_state, LazyAgent(), LazyAgent())
    gsm.step_until_holds(lambda gs: (
        gs.effect_stack.is_not_empty()
        and (
                gs.effect_stack.peek() == AllStatusTriggererEffect(Pid.P1, signal)
                or gs.effect_stack.peek() == AllStatusTriggererEffect(Pid.P2, signal)
        )
    ), observe=observe)
    return gsm.get_game_state()


def use_elemental_aura(
        game_state: GameState,
        element: None | Element,
        pid: Pid,
        char_id: None | int = None,
) -> GameState:
    """ Replace elemental aura of the target character """
    if char_id is None:
        target = StaticTarget.from_player_active(game_state, pid)
    else:
        target = StaticTarget.from_char_id(pid, char_id)
    aura = ElementalAura.from_default()
    if element is not None:
        aura = aura.add(element)
    return game_state.factory().f_player(
        target.pid,
        lambda p: p.factory().f_characters(
            lambda cs: cs.factory().f_character(
                cast(int, target.id),
                lambda c: c.factory().elemental_aura(aura).build()
            ).build()
        ).build()
    ).build()

def active_chars(game_state: GameState) -> tuple[Character, Character]:
    """ Returns the active characters of both players (1 & 2) """
    return (
        game_state.get_player(Pid.P1).just_get_active_character(),
        game_state.get_player(Pid.P2).just_get_active_character(),
    )

def p1_active_char(game_state: GameState) -> Character:
    """ Returns the active character of player 1 """
    return game_state.get_player(Pid.P1).just_get_active_character()

def p2_active_char(game_state: GameState) -> Character:
    """ Returns the active character of player 2 """
    return game_state.get_player(Pid.P2).just_get_active_character()

def p1_chars(game_state: GameState) -> tuple[Character, ...]:
    """ Returns the characters of player 1 """
    return game_state.player1.characters.get_characters()

def p2_chars(game_state: GameState) -> tuple[Character, ...]:
    """ Returns the characters of player 2 """
    return game_state.player2.characters.get_characters()

def end_round(game_state: GameState, pid: Pid) -> GameState:
    """ End round for `pid` given they have not ended yet. """
    game_state = skip_action_round_until(game_state, pid)
    game_state = step_action(game_state, pid, EndRoundAction())
    return game_state
