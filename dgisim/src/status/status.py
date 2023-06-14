from __future__ import annotations
from typing import TypeVar, Union, Optional, ClassVar
from typing_extensions import override
from enum import Enum
from dataclasses import dataclass, replace
from math import ceil

import dgisim.src.effect.effect as eft
import dgisim.src.state.game_state as gs
from dgisim.src.element.element import Element
from dgisim.src.helper.quality_of_life import just, BIG_INT, case_val


class TriggerringEvent(Enum):
    pass


_T = TypeVar('_T', bound="Status")


@dataclass(frozen=True)
class Status:
    class PPType(Enum):
        """ PreProcessType """
        # Damages
        DmgElement = "DmgElement"    # To determine the element
        DmgReaction = "DmgReaction"  # To determine the reaction
        DmgAmount = "DmgNumber"      # To determine final amount of damage

    def __init__(self) -> None:
        if type(self) is Status:  # pragma: no cover
            raise Exception("class Status is not instantiable")

    def preprocess(
            self: _T,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[_T]]:
        """
        Returns the processed Preprocessable and possibly updated or deleted self
        """
        return (item, self)

    # def react_to_event(self, game_state: gs.GameState, event: TriggerringEvent) -> gs.GameState:
    #     raise Exception("TODO")

    def react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> list[eft.Effect]:
        es, new_status = self._react_to_signal(source, signal)
        es, new_status = self._post_react_to_signal(es, new_status)

        import dgisim.src.summon.summon as sm
        # do the removal or update of the status
        if isinstance(self, CharacterTalentStatus) \
                or isinstance(self, EquipmentStatus) \
                or isinstance(self, CharacterStatus):
            if new_status is None:
                es.append(eft.RemoveCharacterStatusEffect(
                    source,
                    type(self),
                ))
            elif new_status != self:
                assert type(self) == type(new_status)
                es.append(eft.UpdateCharacterStatusEffect(
                    source,
                    new_status,  # type: ignore
                ))

        elif isinstance(self, CombatStatus):
            if new_status is None:
                es.append(eft.RemoveCombatStatusEffect(
                    source.pid,
                    type(self),
                ))
            elif new_status != self:
                assert type(self) == type(new_status)
                es.append(eft.UpdateCombatStatusEffect(
                    source.pid,
                    new_status,  # type: ignore
                ))

        elif isinstance(self, sm.Summon):
            if new_status is None:
                es.append(eft.RemoveSummonEffect(
                    source.pid,
                    type(self),
                ))
            elif new_status != self:
                assert type(self) == type(new_status)
                es.append(eft.UpdateSummonEffect(
                    source.pid,
                    new_status,  # type: ignore
                ))

        else:  # pragma: no cover
            raise NotImplementedError

        return es

    def _post_react_to_signal(
            self: _T, effects: list[eft.Effect], new_status: Optional[_T]
    ) -> tuple[list[eft.Effect], Optional[_T]]:
        if new_status != self:
            return effects, new_status
        return effects, self

    def _react_to_signal(
            self: _T, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[_T]]:
        """
        Returns a tuple, containg the effects and updated self (or None if should be removed)
        """
        return [], self

    def same_type_as(self, status: Status) -> bool:
        return type(self) == type(status)

    def update(self: _T, other: _T) -> Optional[_T]:
        new_self = self._update(other)
        return self._post_update(new_self)

    def _post_update(self: _T, new_self: Optional[_T]) -> Optional[_T]:
        return new_self

    def _update(self: _T, other: _T) -> Optional[_T]:
        return self

    def __str__(self) -> str:
        return self.__class__.__name__.removesuffix("Status")  # pragma: no cover


@dataclass(frozen=True)
class CharacterTalentStatus(Status):
    """
    Basic status, describing character talents
    """
    pass


@dataclass(frozen=True)
class EquipmentStatus(Status):
    """
    Basic status, describing weapon, artifact and character unique talents
    """


@dataclass(frozen=True)
class CharacterStatus(Status):
    """
    Basic status, private status to each character
    """
    pass


@dataclass(frozen=True)
class CombatStatus(Status):
    """
    Basic status, status shared across the team
    """
    pass


@dataclass(frozen=True)
class _DurationStatus(Status):
    """
    This class has a duration which acts as a counter
    """
    duration: int
    max_duration: ClassVar[int] = BIG_INT

    @override
    def _post_update(self, new_self: Optional[_DurationStatus]) -> Optional[_DurationStatus]:
        """ remove the status if duration <= 0 """
        if new_self is not None and new_self.duration <= 0:
            new_self = None
        return super()._post_update(new_self)

    @override
    def _update(self, other: _DurationStatus) -> Optional[_DurationStatus]:
        new_duration = min(self.duration + other.duration, self.max_duration)
        return type(self)(duration=new_duration)

    def __str__(self) -> str:
        return super().__str__() + f"({self.duration})"  # pragma: no cover


@dataclass(frozen=True)
class _UsageStatus(Status):
    usages: int
    max_usages: ClassVar[int] = BIG_INT

    @override
    def _post_update(self, new_self: Optional[_UsageStatus]) -> Optional[_UsageStatus]:
        """ remove the status if usages <= 0 """
        if new_self is not None and new_self.usages <= 0:
            new_self = None
        return super()._post_update(new_self)

    @override
    def _update(self, other: _UsageStatus) -> Optional[_UsageStatus]:
        new_usages = min(self.usages + other.usages, self.max_usages)
        return type(self)(usages=new_usages)

    def __str__(self) -> str:
        return super().__str__() + f"({self.usages})"  # pragma: no cover


@dataclass(frozen=True)
class ShieldStatus(Status):
    pass


@dataclass(frozen=True, kw_only=True)
class StackedShieldStatus(ShieldStatus):
    stacks: int
    STACK_LIMIT: ClassVar[Optional[int]] = None
    SHIELD_AMOUNT: ClassVar[int] = 1  # shield amount per stack

    def _is_target(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> bool:
        assert isinstance(item, eft.SpecificDamageEffect)
        if isinstance(self, CharacterTalentStatus) \
                or isinstance(self, EquipmentStatus) \
                or isinstance(self, CharacterStatus):
            return item.target == status_source

        elif isinstance(self, CombatStatus):
            attached_active_character = eft.StaticTarget(
                status_source.pid,
                zone=eft.Zone.CHARACTER,
                id=game_state.get_player(status_source.pid).just_get_active_character().get_id(),
            )
            return item.target == attached_active_character

        else:
            raise NotImplementedError  # pragma: no cover

    @override
    def preprocess(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[StackedShieldStatus]]:
        cls = type(self)
        if signal is Status.PPType.DmgAmount:
            assert isinstance(item, eft.SpecificDamageEffect)
            assert cls.STACK_LIMIT is None or self.stacks <= type(self).STACK_LIMIT  # type: ignore
            if item.damage > 0 \
                    and item.element != Element.PIERCING \
                    and self._is_target(game_state, status_source, item, signal):
                stacks_consumed = min(ceil(item.damage / cls.SHIELD_AMOUNT), self.stacks)
                new_dmg = max(0, item.damage - stacks_consumed * cls.SHIELD_AMOUNT)
                new_item = replace(item, damage=new_dmg)
                new_stacks = self.stacks - stacks_consumed
                if new_stacks == 0:
                    return new_item, None
                else:
                    return new_item, replace(self, stacks=new_stacks)

        return super().preprocess(game_state, status_source, item, signal)

    def __str__(self) -> str:
        return super().__str__() + f"({self.stacks})"  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class CrystallizeStatus(CombatStatus, StackedShieldStatus):
    stacks: int = 1
    STACK_LIMIT: ClassVar[Optional[int]] = 2

    @override
    def update(self, other: CrystallizeStatus) -> Optional[CrystallizeStatus]:
        new_stacks = min(just(type(self).STACK_LIMIT, BIG_INT), self.stacks + other.stacks)
        return type(self)(stacks=new_stacks)


@dataclass(frozen=True)
class DendroCoreStatus(CombatStatus):
    """
    When you deal Pyro DMG or Electro DMG to an opposing active character, DMG dealt +2.
    Usage(s): 1
    =====
    Experiment results:
    - normally the maxinum num of usage(s) is 1
    """
    damage_boost: ClassVar[int] = 2
    usages: int = 1

    @override
    def preprocess(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[DendroCoreStatus]]:
        if signal is Status.PPType.DmgAmount:
            assert isinstance(item, eft.SpecificDamageEffect)
            assert self.usages >= 1
            elem_can_boost = item.element is Element.ELECTRO or item.element is Element.PYRO
            legal_to_boost = status_source.pid is item.source.pid
            target_is_active = item.target.id == game_state.get_player(
                item.target.pid
            ).just_get_active_character().get_id()
            if elem_can_boost and legal_to_boost and target_is_active:
                new_damage = replace(item, damage=item.damage + DendroCoreStatus.damage_boost)
                if self.usages == 1:
                    return new_damage, None
                else:
                    return new_damage, DendroCoreStatus(self.usages - 1)
        return super().preprocess(game_state, status_source, item, signal)

    # @override
    # def update(self, other: DendroCoreStatus) -> DendroCoreStatus:
    #     total_count = min(self.count + other.count, 2)
    #     return DendroCoreStatus(total_count)

    def __str__(self) -> str:
        return super().__str__() + f"({self.usages})"  # pragma: no cover


@dataclass(frozen=True)
class CatalyzingFieldStatus(CombatStatus):
    damage_boost: ClassVar[int] = 1
    usages: int = 2

    @override
    def preprocess(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[CatalyzingFieldStatus]]:
        if signal is Status.PPType.DmgAmount:
            assert isinstance(item, eft.SpecificDamageEffect)
            assert self.usages >= 1
            elem_can_boost = item.element is Element.ELECTRO or item.element is Element.DENDRO
            legal_to_boost = status_source.pid is item.source.pid
            target_is_active = item.target.id == game_state.get_player(
                item.target.pid
            ).just_get_active_character().get_id()
            if elem_can_boost and legal_to_boost and target_is_active:
                new_damage = replace(item, damage=item.damage + CatalyzingFieldStatus.damage_boost)
                if self.usages == 1:
                    return new_damage, None
                else:
                    return new_damage, CatalyzingFieldStatus(self.usages - 1)
        return super().preprocess(game_state, status_source, item, signal)

    def __str__(self) -> str:
        return super().__str__() + f"({self.usages})"  # pragma: no cover


@dataclass(frozen=True)
class FrozenStatus(CharacterStatus):
    damage_boost: ClassVar[int] = 2

    @override
    def preprocess(
            self: _T,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[_T]]:
        if signal is Status.PPType.DmgAmount:
            assert isinstance(item, eft.SpecificDamageEffect)
            can_reaction = item.element is Element.PYRO or item.element is Element.PHYSICAL
            is_damage_target = item.target == status_source
            if is_damage_target and can_reaction:
                return replace(item, damage=item.damage + FrozenStatus.damage_boost), None
        return super().preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[FrozenStatus]]:
        if signal is eft.TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True)
class SatiatedStatus(CharacterStatus):

    @override
    def _react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[SatiatedStatus]]:
        if signal is eft.TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True)
class MushroomPizzaStatus(CharacterStatus, _DurationStatus):
    duration: int = 2

    @override
    def _react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[MushroomPizzaStatus]]:
        es: list[eft.Effect] = []
        d_duration = 0
        if signal is eft.TriggeringSignal.END_ROUND_CHECK_OUT:
            d_duration = -1
            es.append(
                eft.RecoverHPEffect(
                    source,
                    1,
                )
            )
        return es, replace(self, duration=d_duration)


@dataclass(frozen=True)
class JueyunGuobaStatus(CharacterStatus):
    damage_boost: ClassVar[int] = 1
    duration: int = 1

    @override
    def preprocess(
            self: _T,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[_T]]:
        if signal is Status.PPType.DmgAmount:
            assert isinstance(item, eft.SpecificDamageEffect)
            if item.source == status_source and item.damage_type.normal_attack:
                item = replace(item, damage=item.damage + JueyunGuobaStatus.damage_boost)
                return item, None
        return super().preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[JueyunGuobaStatus]]:
        if signal is eft.TriggeringSignal.ROUND_END:
            return [], None
        return [], self


############################## Infusions ##############################


@dataclass(frozen=True, kw_only=True)
class _InfusionStatus(CharacterStatus, _DurationStatus):
    max_duration: ClassVar[int] = BIG_INT
    element: ClassVar[Optional[Element]] = None
    damage_boost: int = 0

    @override
    def preprocess(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.Preprocessable,
            signal: Status.PPType,
    ) -> tuple[eft.Preprocessable, Optional[_InfusionStatus]]:
        assert self.element is not None
        new_item: Optional[eft.SpecificDamageEffect] = None
        if isinstance(item, eft.SpecificDamageEffect):
            if signal is Status.PPType.DmgElement:
                if self._dmg_element_condition(game_state, status_source, item):
                    new_item = replace(item, element=self.element)
            if signal is Status.PPType.DmgAmount:
                if self.damage_boost != 0  \
                        and self._dmg_boost_condition(game_state, status_source, item):
                    new_item = replace(item, damage=item.damage + self.damage_boost)
        if new_item is not None:
            return new_item, self
        else:
            return item, self

    def _dmg_element_condition(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.SpecificDamageEffect,
    ) -> bool:
        return item.element is Element.PHYSICAL \
            and item.damage_type.normal_attack \
            and status_source == item.source \

    def _dmg_boost_condition(
            self,
            game_state: gs.GameState,
            status_source: eft.StaticTarget,
            item: eft.SpecificDamageEffect,
    ) -> bool:
        return item.element is self.element and status_source == item.source

    @override
    def _react_to_signal(
            self, source: eft.StaticTarget, signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[_InfusionStatus]]:
        d_duration = 0
        if signal is eft.TriggeringSignal.ROUND_END:
            d_duration = -1
        return [], replace(self, duration=d_duration)


@dataclass(frozen=True, kw_only=True)
class ElectroInfusionStatus(_InfusionStatus):
    element: ClassVar[Optional[Element]] = Element.ELECTRO


############################## Character specific ##############################


#### Keqing ####

@dataclass(frozen=True, kw_only=True)
class KeqingTalentStatus(CharacterTalentStatus):
    can_infuse: bool

    def _react_to_signal(
            self,
            source: eft.StaticTarget,
            signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[KeqingTalentStatus]]:
        if signal is eft.TriggeringSignal.COMBAT_ACTION:
            return [], type(self)(can_infuse=False)
        return [], self

    def __str__(self) -> str:
        return super().__str__() + f"({case_val(self.can_infuse, 1, 0)})"  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class ThunderingPenanceStatus(EquipmentStatus):
    pass


@dataclass(frozen=True, kw_only=True)
class KeqingElectroInfusionStatus(ElectroInfusionStatus):
    duration: int = 2


#### Kaeya ####


@dataclass(frozen=True, kw_only=True)
class Icicle(CombatStatus, _UsageStatus):
    usages: int = 3

    def _react_to_signal(
            self,
            source: eft.StaticTarget,
            signal: eft.TriggeringSignal
    ) -> tuple[list[eft.Effect], Optional[Icicle]]:
        if source.pid.is_player1() and signal is eft.TriggeringSignal.SWAP_EVENT_1 \
                or source.pid.is_player2() and signal is eft.TriggeringSignal.SWAP_EVENT_2:
            effects: list[eft.Effect] = [
                eft.ReferredDamageEffect(
                    source=source,
                    target=eft.DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.CRYO,
                    damage=2,
                    damage_type=eft.DamageType(status=True),
                ),
                eft.DeathCheckCheckerEffect(),
            ]
            return effects, replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class ColdBloodedStrikeStatus(EquipmentStatus):
    # TODO: detect kaeya elemental skill, react to it and recover hp
    pass
