"""
This file contains the base class "Summon" for all summons,
and implementation of all summons.

Note that a summon is basically a Status.

The classes are divided into 3 sections ordered. Within each section, they are
ordered alphabetically.

- base class, which is Summon
- template classes, starting with an '_', are templates for other classes
- concrete classes, the implementation of summons that are actually in the game
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import ClassVar, Optional, TYPE_CHECKING
from typing_extensions import override, Self

from ..effect import effect as eft
from ..status import status as stt

from ..character.enums import CharacterSkill, CharacterSkillType
from ..effect.enums import TriggeringSignal, DynamicCharacterTarget, Zone
from ..effect.structs import DamageType, StaticTarget
from ..element import Element, Reaction
from ..event import *
from ..helper.quality_of_life import BIG_INT
from ..status.enums import Preprocessables, Informables

if TYPE_CHECKING:
    from ..card.card import Card
    from ..state.game_state import GameState

__all__ = [
    # base
    "Summon",

    # concrete implementations
    "AutumnWhirlwindSummon",
    "BakeKurageSummon",
    "BurningFlameSummon",
    "CelestialDreamsphereSummon",
    "ChainsOfWardingThunderSummon",
    "ClusterbloomArrowSummon",
    "CryoCicinsSummon",
    "CryoHilichurlShooterSummon",
    "CuileinAnbarSummon",
    "DandelionFieldSummon",
    "DrunkenMistSummon",
    "ElectroHilichurlShooterSummon",
    "EyeOfStormyJudgmentSummon",
    "FierySanctumFieldSummon",
    "FrostflakeSekiNoToSummon",
    "GrinMalkinHatSummon",
    "HilichurlBerserkerSummon",
    "HeraldOfFrostSummon",
    "HydroSamachurlSummon",
    "LightfallSwordSummon",
    "LightningRoseSummon",
    "OceanicMimicFrogSummon",
    "OceanicMimicRaptorSummon",
    "OceanicMimicSquirrelSummon",
    "OzSummon",
    "ReflectionSummon",
    "SacredCryoPearlSummon",
    "SesshouSakuraSummon",
    "ShadowswordGallopingFrostSummon",
    "ShadowswordLoneGaleSummon",
    "SolarIsotomaSummon",
    "StormEyeSummon",
    "TalismanSpiritSummon",
    "TenguJuuraiAmbushSummon",
    "TenguJuuraiStormclusterSummon",
    "UshiSummon",
    "YueguiThrowingModeSummon",
]


@dataclass(frozen=True, kw_only=True)
class Summon(stt.Status):
    usages: int = -1

    @override
    def _target_is_self_active(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            target: None | StaticTarget = None,
    ) -> bool:
        active_char = game_state.get_player(status_source.pid).get_active_character()
        if active_char is None:
            return False
        return StaticTarget(
            pid=status_source.pid,
            zone=Zone.CHARACTERS,
            id=active_char.id,
        ) == target

    def __str__(self) -> str:  # pragma: no cover
        return self.__class__.__name__.removesuffix("Summon") + f"({self.usages})"

    def content_repr(self) -> str:
        return f"{self.usages}"


@dataclass(frozen=True, kw_only=True)
class _DestroyOnNumSummon(Summon, stt._UsageStatus):
    pass


@dataclass(frozen=True, kw_only=True)
class _DestoryOnEndNumSummon(Summon):
    @override
    def _post_react_to_signal(
            self, game_state: GameState, effects: list[eft.Effect], new_status: None | Self,
            source: StaticTarget, signal: TriggeringSignal, detail: None | InformableEvent,
    ) -> tuple[list[eft.Effect], None | Self]:
        if new_status is None:
            return super()._post_react_to_signal(game_state, effects, new_status, source, signal, detail)

        if signal is TriggeringSignal.END_ROUND_CHECK_OUT \
                and self.usages + new_status.usages <= 0:
            return super()._post_react_to_signal(game_state, effects, None, source, signal, detail)

        return super()._post_react_to_signal(game_state, effects, new_status, source, signal, detail)


@dataclass(frozen=True, kw_only=True)
class _DmgPerRoundSummon(_DestroyOnNumSummon):
    usages: int = -1
    MAX_USAGES: ClassVar[int] = BIG_INT
    DMG: ClassVar[int] = 0
    ELEMENT: ClassVar[Element]
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        es: list[eft.Effect] = []
        d_usages = 0
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            d_usages = -1
            es.append(
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=self.ELEMENT,
                    damage=self.DMG,
                    damage_type=DamageType(summon=True),
                )
            )
        if d_usages == 0:
            return es, self
        return es, replace(self, usages=d_usages)


@dataclass(frozen=True, kw_only=True)
class _TeamDmgPerRoundSummon(_DmgPerRoundSummon):
    OFF_FIELD_ELEM: ClassVar[Element] = Element.PIERCING
    OFF_FIELD_DMG: ClassVar[int]

    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        es: list[eft.Effect] = []
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            es.append(
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_OFF_FIELD,
                    element=self.OFF_FIELD_ELEM,
                    damage=self.OFF_FIELD_DMG,
                    damage_type=DamageType(summon=True),
                )
            )
        super_es, new_self = super()._react_to_signal(game_state, source, signal, detail)
        return es + super_es, new_self


@dataclass(frozen=True, kw_only=True)
class _ConvertableAnemoSummon(_DestroyOnNumSummon):
    usages: int = -1
    MAX_USAGES: ClassVar[int] = BIG_INT
    curr_elem: Element = Element.ANEMO
    ready_elem: None | Element = None
    DMG: ClassVar[int]
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    def _convertable(self) -> bool:
        return self.curr_elem is Element.ANEMO

    def _to_be_converted(self) -> bool:
        return self._convertable() and self.ready_elem is not None

    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if isinstance(information, DmgIEvent):
            damage = information.dmg
            if (
                    self._convertable()
                    and damage.source.pid is status_source.pid
                    and (
                        damage.damage_type.directly_from_character()
                        or damage.damage_type.directly_from_summon()
                    )
                    and damage.reaction is not None
                    and damage.reaction.reaction_type is Reaction.SWIRL
            ):
                return replace(
                    self,
                    ready_elem=damage.reaction.first_elem,
                )
        return self

    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        es: list[eft.Effect] = []
        new_self = self
        if signal is TriggeringSignal.POST_SKILL:
            if self._to_be_converted():
                assert self.ready_elem is not None
                new_self = replace(
                    self,
                    usages=0,  # this is delta-usages
                    curr_elem=self.ready_elem,
                    ready_elem=None
                )
                return [], new_self

        elif signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            if self._to_be_converted():
                assert self.ready_elem is not None
                new_self = replace(
                    self,
                    usages=0,  # this is delta-usages
                    curr_elem=self.ready_elem,
                    ready_elem=None,
                )
                es.append(eft.UpdateSummonEffect(source.pid, new_self))
            es.append(
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=new_self.curr_elem,
                    damage=new_self.DMG,
                    damage_type=DamageType(summon=True),
                )
            )
            if new_self._convertable():
                opponent_aura = (
                    game_state
                    .get_player(source.pid.other)
                    .just_get_active_character()
                    .elemental_aura
                )
                reaction = Reaction.consult_reaction_with_aura(opponent_aura, Element.ANEMO)
                if reaction is not None and reaction.first_elem in Reaction.SWIRL.first_elems:
                    new_self = replace(
                        new_self,
                        curr_elem=reaction.first_elem,
                        ready_elem=None,
                    )
            new_self = replace(
                new_self,
                usages=-1,
            )

        return es, new_self

    def _update(self, other: Self) -> Self | None:
        new_usage = min(self.usages + other.usages, max(self.usages, self.MAX_USAGES))
        return replace(other, usages=new_usage)

    def __str__(self) -> str:  # pragma: no cover
        return super().__str__() + f"({self.curr_elem}|{self.ready_elem})"

    def content_repr(self) -> str:
        return f"{self.usages}, {self.curr_elem}|{self.ready_elem}"


@dataclass(frozen=True, kw_only=True)
class AutumnWhirlwindSummon(_ConvertableAnemoSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1


@dataclass(frozen=True, kw_only=True)
class BakeKurageSummon(_DestroyOnNumSummon):
    usages: int = 2
    # activated: bool = False
    MAX_USAGES: ClassVar[int] = 2
    BASE_DMG: ClassVar[int] = 1
    ADDITIONAL_DMG_BOOST: ClassVar[int] = 1
    HEAL_AMOUNT: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.HYDRO
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        # TriggeringSignal.COMBAT_ACTION,
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    # @override
    # def _inform(
    #         self,
    #         game_state: GameState,
    #         status_source: StaticTarget,
    #         info_type: Informables,
    #         information: InformableEvent,
    # ) -> Self:
    #     if info_type is Informables.POST_SKILL_USAGE:
    #         assert isinstance(information, SkillIEvent)
    #         if not (
    #                 information.source.pid is status_source.pid
    #                 and information.skill_type is CharacterSkill.ELEMENTAL_BURST
    #                 and not self.activated
    #         ):
    #             return self
    #         char = game_state.get_character_target(information.source)
    #         from ..character.character import SangonomiyaKokomi
    #         if isinstance(char, SangonomiyaKokomi) and char.talent_equipped():
    #             return replace(self, activated=True)
    #     return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        # if signal is TriggeringSignal.COMBAT_ACTION and self.activated:
        #     return [], replace(self, usages=self.MAX_USAGES, activated=False)
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            self_chars = game_state.get_player(source.pid).characters
            activate_additional_dmg_boost = any(
                (
                    stt.CeremonialGarmentStatus in char.character_statuses
                    and char.talent_equipped()
                )
                for char in self_chars
            )
            return [
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=self.ELEMENT,
                    damage=self.BASE_DMG + (
                        self.ADDITIONAL_DMG_BOOST
                        if activate_additional_dmg_boost
                        else 0
                    ),
                    damage_type=DamageType(summon=True),
                ),
                eft.RecoverHPEffect(
                    source=StaticTarget.from_summon(source.pid, type(self)),
                    target=StaticTarget.from_char_id(
                        source.pid, self_chars.just_get_active_character_id()
                    ),
                    recovery=self.HEAL_AMOUNT,
                ),
            ], replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class BurningFlameSummon(_DmgPerRoundSummon):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.PYRO


@dataclass(frozen=True, kw_only=True)
class CelestialDreamsphereSummon(_DmgPerRoundSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.CRYO

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        es, new_self = super()._react_to_signal(game_state, source, signal, detail)
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            if stt.ShootingStarStatus in game_state.get_player(source.pid).combat_statuses:
                return es + [
                    eft.UpdateCombatStatusEffect(
                        target_pid=source.pid,
                        status=stt.ShootingStarStatus(usages=1),
                    ),
                ], new_self
        return es, new_self


@dataclass(frozen=True, kw_only=True)
class ChainsOfWardingThunderSummon(_DmgPerRoundSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    swap_reduce_usages: int = 1
    SWAP_REDUCE_MAX_USAGES: int = 1
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.ELECTRO
    COST_RAISE: ClassVar[int] = 1

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        *_DmgPerRoundSummon.REACTABLE_SIGNALS,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SWAP_COST_ANY:
            assert isinstance(item, ActionPEvent) and item.event_type is EventType.SWAP
            if item.source.pid is status_source.pid.other \
                    and self.swap_reduce_usages > 0:
                assert item.dice_cost.num_dice() == item.dice_cost[Element.ANY]
                new_cost = item.dice_cost + {Element.ANY: self.COST_RAISE}
                return replace(item, dice_cost=new_cost), replace(
                    self, swap_reduce_usages=self.swap_reduce_usages - 1
                )
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        es, new_self = super()._react_to_signal(game_state, source, signal, detail)
        if new_self is None:
            return es, None
        if signal is TriggeringSignal.ROUND_END \
                and new_self.swap_reduce_usages < self.SWAP_REDUCE_MAX_USAGES:
            return es, replace(new_self, usages=0, swap_reduce_usages=self.SWAP_REDUCE_MAX_USAGES)
        return es, new_self

    def content_repr(self) -> str:
        return super().content_repr() + f",{self.swap_reduce_usages}"


@dataclass(frozen=True, kw_only=True)
class ClusterbloomArrowSummon(_DmgPerRoundSummon):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.DENDRO


@dataclass(frozen=True, kw_only=True)
class CryoCicinsSummon(_DmgPerRoundSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 3
    DMG: ClassVar[int] = 1
    TALENT_DMG: ClassVar[int] = 2
    ELEMENT: ClassVar[Element] = Element.CRYO
    normal_attacked: bool = False  # True if normal attack is used by FatuiCryoCicinMage
    exceeded: bool = False  # True if talent is equipped and usages will exceed MAX_USAGES
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        *_DmgPerRoundSummon.REACTABLE_SIGNALS,
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.POST_DMG,
    ))

    @override
    def add(self, other: type[Self]) -> None | Self:
        return self.update(replace(self, usages=2))

    @override
    def _inform(
            self, game_state: GameState, status_source: StaticTarget, info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.PRE_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            from ..character.character import FatuiCryoCicinMage
            char = game_state.get_character_target(information.source)
            if not (
                    information.source.pid is status_source.pid
                    and isinstance(char, FatuiCryoCicinMage)
            ):
                return self
            usages_addition = 0
            if information.skill_true_type is CharacterSkillType.NORMAL_ATTACK:
                usages_addition = 1
            elif information.skill_type is CharacterSkill.SKILL2:
                usages_addition = 2
            future_usages = self.usages + usages_addition
            if future_usages > self.MAX_USAGES and char.talent_equipped():
                # here we assume it is safe to ignore usages addition caused by normal attack
                return replace(self, exceeded=True)
            elif information.skill_true_type is CharacterSkillType.NORMAL_ATTACK:
                return replace(self, normal_attacked=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        es, new_self = super()._react_to_signal(game_state, source, signal, detail)
        if signal is TriggeringSignal.POST_DMG:
            assert isinstance(detail, DmgIEvent)
            from ..character.character import FatuiCryoCicinMage
            target_char = game_state.get_character_target(detail.dmg.target)
            if (
                    detail.dmg.target.pid == source.pid
                    and isinstance(target_char, FatuiCryoCicinMage)
                    and detail.dmg.reaction is not None
            ):
                return [], replace(self, usages=-1)
        elif signal is TriggeringSignal.POST_SKILL:
            if self.exceeded:
                return [
                    eft.ReferredDamageEffect(
                        source=source,
                        target=DynamicCharacterTarget.OPPO_ACTIVE,
                        element=self.ELEMENT,
                        damage=self.TALENT_DMG,
                        damage_type=DamageType(summon=True),
                    )
                ], replace(self, usages=0, exceeded=False)
            elif self.normal_attacked:
                return [], replace(self, usages=1, normal_attacked=False)
        return es, new_self

    @override
    def content_repr(self) -> str:
        return (
            f"{self.usages}"
            + f"{' atked' if self.normal_attacked else ''}{' exceeded' if self.exceeded else ''}"
        )


@dataclass(frozen=True, kw_only=True)
class CryoHilichurlShooterSummon(_DmgPerRoundSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.CRYO


@dataclass(frozen=True, kw_only=True)
class CuileinAnbarSummon(_DmgPerRoundSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 2
    ELEMENT: ClassVar[Element] = Element.DENDRO


@dataclass(frozen=True, kw_only=True)
class DandelionFieldSummon(_DestroyOnNumSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DAMAGE_AMOUNT: ClassVar[int] = 1
    DAMAGE_ELEM: ClassVar[Element] = Element.ANEMO
    DAMAGE_BOOST: ClassVar[int] = 1
    HEAL_AMOUNT: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if not (
                    dmg.source.pid is status_source.pid
                    and dmg.element is Element.ANEMO
                    and dmg.damage_type.directly_from_character()
            ):
                return item, self
            self_chars = game_state.get_player(status_source.pid).characters
            from ..character.character import Jean
            if any(
                isinstance(char, Jean) and char.talent_equipped()
                for char in self_chars
            ):
                return item.delta_damage(self.DAMAGE_BOOST), self
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            return [
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=self.DAMAGE_ELEM,
                    damage=self.DAMAGE_AMOUNT,
                    damage_type=DamageType(summon=True),
                ),
                eft.RecoverHPEffect(
                    source=StaticTarget.from_summon(source.pid, type(self)),
                    target=StaticTarget.from_player_active(game_state, source.pid),
                    recovery=self.HEAL_AMOUNT,
                ),
            ], replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class DrunkenMistSummon(_DmgPerRoundSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.CRYO

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        es, new_self = super()._react_to_signal(game_state, source, signal, detail)
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            es.append(
                eft.RecoverHPEffect(
                    source=StaticTarget.from_summon(source.pid, type(self)),
                    target=StaticTarget.from_player_active(game_state, source.pid),
                    recovery=2,
                )
            )
        return es, new_self


@dataclass(frozen=True, kw_only=True)
class ElectroHilichurlShooterSummon(_DmgPerRoundSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.ELECTRO


@dataclass(frozen=True, kw_only=True)
class EyeOfStormyJudgmentSummon(_DmgPerRoundSummon):
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 3
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.ELECTRO

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            if (
                    item.dmg.source.pid is status_source.pid
                    and item.dmg.damage_type.direct_elemental_burst()
            ):
                return item.delta_damage(1), self
        return item, self


@dataclass(frozen=True, kw_only=True)
class FierySanctumFieldSummon(_DmgPerRoundSummon, stt._ShieldStatus):
    usages: int = 3
    activated: bool = False
    shield_usages: int = 1
    SHIELD_AMOUNT: ClassVar[int] = 1
    MAX_USAGES: ClassVar[int] = 3
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.PYRO

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        *_DmgPerRoundSummon.REACTABLE_SIGNALS,
        TriggeringSignal.POST_DMG,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_MINUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            char = game_state.get_character_target(dmg.target)
            from ..character.character import Dehya
            if not (
                    dmg.target.pid is status_source.pid
                    and self.shield_usages > 0
                    and dmg.damage > 0
                    and char is not None
                    and type(char) is not Dehya
            ):
                return item, self
            return (
                item.delta_damage(-self.SHIELD_AMOUNT),
                replace(self, shield_usages=self.shield_usages - 1, activated=True),
            )
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        es, new_self = super()._react_to_signal(game_state, source, signal, detail)
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT and new_self is not None:
            new_self = replace(new_self, shield_usages=1)
        elif signal is TriggeringSignal.POST_DMG and self.activated:
            from ..character.character import Dehya
            assert isinstance(detail, DmgIEvent)
            if detail.dmg.target != source:
                dehya = game_state.get_player(source.pid).characters.find_first_character(Dehya)
                if dehya is not None and dehya.hp >= 7:
                    es.append(eft.SpecificDamageEffect(
                        source=source,
                        target=StaticTarget.from_char_id(source.pid, dehya.id),
                        element=Element.PIERCING,
                        damage=1,
                        damage_type=DamageType(summon=True),
                    ))
                if new_self is not None:
                    new_self = replace(new_self, activated=False)
        return es, new_self

@dataclass(frozen=True, kw_only=True)
class FrostflakeSekiNoToSummon(_DmgPerRoundSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 2
    ELEMENT: ClassVar[Element] = Element.CRYO


@dataclass(frozen=True, kw_only=True)
class GrinMalkinHatSummon(_DmgPerRoundSummon):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.PYRO


@dataclass(frozen=True, kw_only=True)
class HilichurlBerserkerSummon(_DestroyOnNumSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 2
    ELEMENT: ClassVar[Element] = Element.PYRO


@dataclass(frozen=True, kw_only=True)
class HeraldOfFrostSummon(_DmgPerRoundSummon):
    usages: int = 3
    activated: bool = False
    one_time_healing_available: bool = True
    MAX_USAGES: ClassVar[int] = 3
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.CRYO
    HEAL_AMOUNT: ClassVar[int] = 1

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        *_DmgPerRoundSummon.REACTABLE_SIGNALS,
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _inform(
            self, game_state: GameState, status_source: StaticTarget, info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            from ..character.character import Qiqi
            if not self.activated and information.is_skill_from_character(
                    game_state,
                    status_source.pid,
                    CharacterSkill.SKILL1,
                    Qiqi,
            ):
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.activated:
            self_alive_chars = game_state.get_player(
                source.pid
            ).characters.get_alive_character_in_activity_order()
            most_damage = max(char.hp_lost() for char in self_alive_chars)
            if most_damage == 0:
                return [], replace(self, usages=0, activated=False)
            char_to_heal = next(
                char
                for char in self_alive_chars
                if char.hp_lost() == most_damage
            )
            recoveries: list[eft.Effect] = [
                eft.RecoverHPEffect(
                    source=StaticTarget.from_summon(source.pid, type(self)),
                    target=StaticTarget.from_char_id(source.pid, char_to_heal.id),
                    recovery=self.HEAL_AMOUNT,
                ),
            ]
            return recoveries, replace(self, usages=0, activated=False)
        elif signal is TriggeringSignal.DIRECT_TRIGGER and self.one_time_healing_available:
            if any(
                    char.hp_lost() > 0
                    for char in game_state.get_player(source.pid).characters.get_alive_characters()
            ):
                return [
                    eft.RecoverHPEffect(
                        source=StaticTarget.from_summon(source.pid, type(self)),
                        target=StaticTarget.from_player_active(game_state, source.pid),
                        recovery=self.HEAL_AMOUNT,
                    ),
                ], replace(self, usages=0, one_time_healing_available=False)
        elif signal is TriggeringSignal.ROUND_END and not self.one_time_healing_available:
            return [], replace(self, usages=0, one_time_healing_available=True)
        return super()._react_to_signal(game_state, source, signal, detail)

    @override
    def react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent = None,
    ) -> list[eft.Effect]:
        es = super().react_to_signal(game_state, source, signal, detail)
        if signal is TriggeringSignal.POST_SKILL and self.activated and self.one_time_healing_available:
            es.append(eft.TriggerSummonEffect(source.pid, type(self), TriggeringSignal.DIRECT_TRIGGER))
        return es

    @override
    def content_repr(self) -> str:
        return f"{self.usages}{' | *' if self.one_time_healing_available else ''}"


@dataclass(frozen=True, kw_only=True)
class HydroSamachurlSummon(_DestroyOnNumSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.HYDRO


@dataclass(frozen=True, kw_only=True)
class LightfallSwordSummon(Summon, stt._UsageStatus):
    usages: int = 0
    skill_used: None | CharacterSkillType = None
    skill_source_id: None | int = None
    AUTO_DESTROY: ClassVar[bool] = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if not (
                    information.source.pid is status_source.pid
                    and (
                        information.skill_true_type.is_normal_attack()
                        or information.skill_true_type.is_elemental_skill()
                    )
            ):
                return self
            source_char = game_state.get_character_target(information.source)
            if source_char is None:
                return self
            from ..character.character import Eula
            if isinstance(source_char, Eula):
                assert isinstance(information.source.id, int)
                return replace(
                    self,
                    skill_used=information.skill_true_type,
                    skill_source_id=information.source.id,
                )
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.skill_used is not None:
            assert self.skill_source_id is not None
            source_char = game_state.get_character_target(
                StaticTarget.from_char_id(source.pid, self.skill_source_id)
            )
            from ..character.character import Eula
            if not (
                    source_char is not None
                    and source_char.is_alive()
                    and isinstance(source_char, Eula)
            ):
                return [], self
            if self.skill_used is CharacterSkillType.ELEMENTAL_SKILL and source_char.talent_equipped():
                return [], replace(self, usages=3, skill_used=None, skill_source_id=None)
            return [], replace(self, usages=2, skill_used=None, skill_source_id=None)
        elif signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            return [
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.PHYSICAL,
                    damage=3 + self.usages,
                    damage_type=DamageType(summon=True),
                )
            ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class LightningRoseSummon(_DmgPerRoundSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 2
    ELEMENT: ClassVar[Element] = Element.ELECTRO


@dataclass(frozen=True, kw_only=True)
class OceanicMimicFrogSummon(_DestoryOnEndNumSummon, stt.FixedShieldStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    AUTO_DESTROY: ClassVar[bool] = False
    SHIELD_AMOUNT: ClassVar[int] = 1
    DMG: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        es: list[eft.Effect] = []
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT \
                and self.usages == 0:
            es.append(
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.HYDRO,
                    damage=self.DMG,
                    damage_type=DamageType(summon=True),
                )
            )
            return es, None

        return es, self


@dataclass(frozen=True, kw_only=True)
class OceanicMimicRaptorSummon(_DmgPerRoundSummon):
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 3
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.HYDRO


@dataclass(frozen=True, kw_only=True)
class OceanicMimicSquirrelSummon(_DmgPerRoundSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 2
    ELEMENT: ClassVar[Element] = Element.HYDRO


@dataclass(frozen=True, kw_only=True)
class OzSummon(_DmgPerRoundSummon):
    usages: int = 2
    activated: bool = False
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1
    ACTIVATED_DMG: ClassVar[int] = 2
    ELEMENT: ClassVar[Element] = Element.ELECTRO
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        *_DmgPerRoundSummon.REACTABLE_SIGNALS,
        TriggeringSignal.POST_SKILL,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            from ..character.character import Fischl
            if not self.activated and information.is_skill_from_character(
                    game_state,
                    status_source.pid,
                    CharacterSkill.SKILL1,
                    Fischl,
            ):
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        if signal is TriggeringSignal.POST_SKILL and self.activated:
            return [
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=self.ELEMENT,
                    damage=self.ACTIVATED_DMG,
                    damage_type=DamageType(summon=True),
                ),
            ], replace(self, usages=-1, activated=False)
        return super()._react_to_signal(game_state, source, signal, detail)


@dataclass(frozen=True, kw_only=True)
class ReflectionSummon(_DestoryOnEndNumSummon, stt.FixedShieldStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    AUTO_DESTROY: ClassVar[bool] = False
    SHIELD_AMOUNT: ClassVar[int] = 1
    DMG: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        es: list[eft.Effect] = []
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            es.append(
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.HYDRO,
                    damage=self.DMG,
                    damage_type=DamageType(summon=True),
                )
            )
            return es, None

        return es, self


@dataclass(frozen=True, kw_only=True)
class SacredCryoPearlSummon(_TeamDmgPerRoundSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.CRYO
    OFF_FIELD_ELEM: ClassVar[Element] = Element.PIERCING
    OFF_FIELD_DMG: ClassVar[int] = 1


@dataclass(frozen=True, kw_only=True)
class SesshouSakuraSummon(_DestroyOnNumSummon):
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 6
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.ELECTRO
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.END_ROUND_CHECK_OUT,
        TriggeringSignal.SELF_DECLARE_END_ROUND,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        es: list[eft.Effect] = []
        d_usages = 0
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            d_usages = -1
            es.append(
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=self.ELEMENT,
                    damage=self.DMG,
                    damage_type=DamageType(summon=True),
                )
            )
        elif signal is TriggeringSignal.SELF_DECLARE_END_ROUND:
            if self.usages >= 4:
                d_usages = -1
                es.append(
                    eft.ReferredDamageEffect(
                        source=source,
                        target=DynamicCharacterTarget.OPPO_ACTIVE,
                        element=self.ELEMENT,
                        damage=self.DMG,
                        damage_type=DamageType(summon=True),
                    )
                )
        if d_usages == 0:
            return es, self
        return es, replace(self, usages=d_usages)


@dataclass(frozen=True, kw_only=True)
class _ShadowswordBaseSummon(_DmgPerRoundSummon):
    usages: int = 2
    activated: bool = False
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        *_DmgPerRoundSummon.REACTABLE_SIGNALS,
        TriggeringSignal.POST_SKILL,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            from ..character.character import MaguuKenki
            if not self.activated and information.is_skill_from_character(
                    game_state,
                    status_source.pid,
                    CharacterSkill.ELEMENTAL_BURST,
                    MaguuKenki,
            ):
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.activated:
            return [
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=self.ELEMENT,
                    damage=self.DMG,
                    damage_type=DamageType(summon=True),
                ),
            ], replace(self, usages=0, activated=False)
        return super()._react_to_signal(game_state, source, signal, detail)


@dataclass(frozen=True, kw_only=True)
class ShadowswordGallopingFrostSummon(_ShadowswordBaseSummon):
    ELEMENT: ClassVar[Element] = Element.CRYO


@dataclass(frozen=True, kw_only=True)
class ShadowswordLoneGaleSummon(_ShadowswordBaseSummon):
    ELEMENT: ClassVar[Element] = Element.ANEMO


@dataclass(frozen=True, kw_only=True)
class SolarIsotomaSummon(_DmgPerRoundSummon):
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 3
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.GEO
    COST_DEDUCTION: ClassVar[int] = 1
    DMG_BOOST: ClassVar[int] = 1

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SKILL_COST_ANY:
            assert isinstance(item, ActionPEvent)
            from ..character.character import Albedo
            if not (
                    item.source.pid is status_source.pid
                    and item.event_sub_type is CharacterSkillType.NORMAL_ATTACK
                    and item.dice_cost.can_cost_less_any()
                    and self._some_char_equiped_talent(game_state, status_source.pid, Albedo)
            ):
                return item, self
            if self._player_can_plunge(game_state, status_source.pid):
                new_item = replace(
                    item,
                    dice_cost=item.dice_cost.cost_less_any(self.COST_DEDUCTION),
                )
                return new_item, self
        elif signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            from ..character.character import Albedo
            if (
                    dmg.source.pid is status_source.pid
                    and dmg.damage_type.direct_plunge_attack()
                    and self._some_char_equiped_talent(game_state, status_source.pid, Albedo)
            ):
                return item.delta_damage(self.DMG_BOOST), self
        elif signal is Preprocessables.SWAP:
            assert isinstance(item, ActionPEvent)
            if item.source.pid is status_source.pid and item.is_combat_action():
                return item.make_fast_action(), self

        return item, self


@dataclass(frozen=True, kw_only=True)
class StormEyeSummon(_ConvertableAnemoSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 2

    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], Optional[Self]]:
        es, new_self = super()._react_to_signal(game_state, source, signal, detail)
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            oppo_active_char_id = game_state.get_player(
                source.pid.other
            ).just_get_active_character().id
            self_active_char_id = game_state.get_player(
                source.pid
            ).just_get_active_character().id
            id_diff = self_active_char_id - oppo_active_char_id
            if id_diff < 0:
                es.append(eft.BackwardSwapCharacterEffect(
                    target_player=source.pid.other,
                ))
            elif id_diff > 0:
                es.append(eft.ForwardSwapCharacterEffect(
                    target_player=source.pid.other,
                ))
        return es, new_self


@dataclass(frozen=True, kw_only=True)
class TalismanSpiritSummon(_DmgPerRoundSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.CRYO
    DMG_BOOST: ClassVar[int] = 1

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if not (
                    dmg.target.pid is status_source.pid.other
                    and (
                        dmg.element is Element.CRYO
                        or dmg.element is Element.PHYSICAL
                    )
            ):
                return item, self
            dmg = replace(dmg, damage=dmg.damage + self.DMG_BOOST)
            return DmgPEvent(dmg=dmg), self
        return super()._preprocess(game_state, status_source, item, signal)


@dataclass(frozen=True, kw_only=True)
class _TenguJuuraiSummon(_DmgPerRoundSummon):
    ELEMENT: ClassVar[Element] = Element.ELECTRO

    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        es, new_self = super()._react_to_signal(game_state, source, signal, detail)
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            es.append(
                eft.RelativeAddCharacterStatusEffect(
                    source_pid=source.pid,
                    target=DynamicCharacterTarget.SELF_ACTIVE,
                    status=stt.CrowfeatherCoverStatus,
                ),
            )
        return es, new_self


@dataclass(frozen=True, kw_only=True)
class TenguJuuraiAmbushSummon(_TenguJuuraiSummon):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    DMG: ClassVar[int] = 1


@dataclass(frozen=True, kw_only=True)
class TenguJuuraiStormclusterSummon(_TenguJuuraiSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 2


@dataclass(frozen=True, kw_only=True)
class UshiSummon(_DestoryOnEndNumSummon, stt.FixedShieldStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    AUTO_DESTROY: ClassVar[bool] = False
    SHIELD_AMOUNT: ClassVar[int] = 1
    DMG: ClassVar[int] = 1
    status_gaining_usages: int = 1
    status_gaining_triggered: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.END_ROUND_CHECK_OUT,
        TriggeringSignal.POST_DMG,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.DMG_DEALT:
            assert isinstance(information, DmgIEvent)
            if (
                    self._is_target(game_state, status_source, information.dmg)
                    and self.status_gaining_usages > 0
                    and not self.status_gaining_triggered
            ):
                return replace(self, status_gaining_triggered=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            return [
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.GEO,
                    damage=self.DMG,
                    damage_type=DamageType(summon=True),
                )
            ], None

        elif signal is TriggeringSignal.POST_DMG and self.status_gaining_triggered:
            assert self.status_gaining_usages > 0

            # if active char is defeated, do nothing
            active_char = game_state.get_player(source.pid).get_active_character()
            assert active_char is not None, (source, game_state)
            if active_char.is_defeated():
                return [], replace(self, usages=0, status_gaining_triggered=False)

            from ..character.character import AratakiItto
            itto = game_state.get_player(
                source.pid
            ).characters.find_first_character(AratakiItto)
            effects: list[eft.Effect] = []
            if itto is not None and itto.alive:
                effects.append(eft.AddCharacterStatusEffect(
                    target=StaticTarget.from_char_id(source.pid, itto.id),
                    status=stt.SuperlativeSuperstrengthStatus
                ))
            return effects, replace(
                self,
                usages=0,
                status_gaining_usages=self.status_gaining_usages - 1,
                status_gaining_triggered=False,
            )

        return [], self


@dataclass(frozen=True, kw_only=True)
class YueguiThrowingModeSummon(_DestroyOnNumSummon):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG: ClassVar[int] = 1
    HEALING: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.DENDRO
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            from ..character.character import Yaoyao
            characters = game_state.get_player(source.pid).characters
            yaoyao = characters.find_first_character(Yaoyao)
            dmg, healing = 0, 0
            if yaoyao is not None and yaoyao.talent_equipped() and self.usages == 1:
                dmg, healing = 1, 1
            chars_by_dmg_taken = sorted(
                characters.get_alive_character_in_activity_order(),
                key=lambda c: c.hp_lost(),
                reverse=True,
            )
            char_target = StaticTarget.from_char_id(source.pid, chars_by_dmg_taken[0].id)
            return [
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=self.ELEMENT,
                    damage=self.DMG + dmg,
                    damage_type=DamageType(summon=True),
                ),
                eft.RecoverHPEffect(
                    source=source,
                    target=char_target,
                    recovery=self.HEALING + healing,
                ),
            ], replace(self, usages=-1)
        return [], self
