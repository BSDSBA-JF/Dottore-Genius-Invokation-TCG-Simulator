"""
This file contains the base class "Status" for all statuses,
and implementation of all statuses.

The classes are divided into 4 sections ordered. Within each section, they are
ordered alphabetically.

- base class, which is Status
- type classes, used to identify what type of status a status is
- template classes, starting with an '_', are templates for other classes
- concrete classes, the implementation of statuses that are actually in the game
"""
from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass, fields, replace
from enum import Enum
from functools import cached_property
from itertools import chain
from math import ceil
from typing import ClassVar, cast, TYPE_CHECKING
from typing_extensions import override, Self

from ..effect import effect as eft

from ..character.enums import CharacterSkill, CharacterSkillType, WeaponType
from ..dice import ActualDice
from ..effect.effects_template import budget_post_effect, standard_post_effects
from ..effect.enums import Zone, TriggeringSignal, DynamicCharacterTarget
from ..effect.structs import StaticTarget, DamageType
from ..element import Element, Reaction
from ..event import *
from ..helper.hashable_dict import HashableDict
from ..helper.quality_of_life import BIG_INT, cached_classproperty, case_val
from .enums import Preprocessables, Informables

if TYPE_CHECKING:
    from ..card import card as crd
    from ..card.card import Card
    from ..character.character import Character
    from ..encoding.encoding_plan import EncodingPlan
    from ..state.enums import Pid
    from ..state.game_state import GameState

__all__ = [
    # base
    "Status",

    # type
    "PlayerHiddenStatus",
    "PersonalStatus",
    "CharacterHiddenStatus",  # it should be statuses used to record character-talent related data
    "EquipmentStatus",  # talent / weapon / artifact
    "TalentEquipmentStatus",
    "WeaponEquipmentStatus",
    "ArtifactEquipmentStatus",
    "CharacterStatus",  # statues that belongs to one character only
    "CombatStatus",  # statues that buffs the active character

    # templates & types
    "StackedShieldStatus",
    "FixedShieldStatus",
    "PrepareSkillStatus",
    "RevivalStatus",

    # hidden status
    "ArcaneLegendUsedStatus",
    "ChargedAttackStatus",
    "PlungeAttackStatus",
    "DeathThisRoundStatus",

    # equipment status
    ## Weapon ##
    ### bow ###
    "AmosBowStatus",
    "ElegyForTheEndStatus",
    "KingsSquireStatus",
    "RavenBowStatus",
    "SacrificialBowStatus",
    ### catalyst ###
    "AThousandFloatingDreamsStatus",
    "FruitOfFulfillmentStatus",
    "MagicGuideStatus",
    "SacrificialFragmentsStatus",
    ### claymore ###
    "SacrificialGreatswordStatus",
    "TheBellStatus",
    "WhiteIronGreatswordStatus",
    "WolfsGravestoneStatus",
    ### polearm ###
    "EngulfingLightningStatus",
    "LithicSpearStatus",
    "MoonpiercerStatus",
    "VortexVanquisherStatus",
    "WhiteTasselStatus",
    ### sword ###
    "AquilaFavoniaStatus",
    "FavoniusSwordStatus",
    "SacrificialSwordStatus",
    "TravelersHandySwordStatus",
    ## Artifact ##
    "ArchaicPetraStatus",
    "BlizzardStrayerStatus",
    "BrokenRimesEchoStatus",
    "CrimsonWitchOfFlamesStatus",
    "CrownOfWatatsumiStatus",
    "DeepwoodMemoriesStatus",
    "EchoesOfAnOfferingStatus",
    "EmblemOfSeveredFateStatus",
    "ExilesCircletStatus",
    "FlowingRingsStatus",
    "GamblersEarringsStatus",
    "GeneralsAncientHelmStatus",
    "GildedDreamsStatus",
    "HeartOfDepthStatus",
    "HeartOfKhvarenasBrillianceStatus",
    "InstructorsCapStatus",
    "LaurelCoronetStatus",
    "MaskOfSolitudeBasaltStatus",
    "OceanHuedClamStatus",
    "OrnateKabutoStatus",
    "ShadowOfTheSandKingStatus",
    "ThunderSummonersCrownStatus",
    "ThunderingFuryStatus",
    "TenacityOfTheMillelithStatus",
    "ViridescentVenererStatus",
    "ViridescentVenerersDiademStatus",
    "VourukashasGlowStatus",
    "WineStainedTricorneStatus",
    "WitchsScorchingHatStatus",

    # Combat Status
    "AncientCourtyardStatus",
    "CatalyzingFieldStatus",
    "ChangingShiftsStatus",
    "CrystallizeStatus",
    "DendroCoreStatus",
    "IHaventLostYetOnCooldownStatus",
    "ElementalResonanceEnduringRockStatus",
    "ElementalResonanceFerventFlamesStatus",
    "ElementalResonanceShatteringIceStatus",
    "ElementalResonanceSprawlingGreeneryStatus",
    "FreshWindOfFreedomStatus",
    "LeaveItToMeStatus",
    "LyresongStatus",
    "MillennialMovementFarewellSongStatus",
    "PassingOfJudgmentStatus",
    "RebelliousShieldStatus",
    "RedFeatherFanStatus",
    "ReviveOnCooldownStatus",
    "SandAndDreamsStatus",
    "StoneAndContractsStatus",
    "SunyataFlowerStatus",
    "TheBoarPrincessStatus",
    "WhenTheCraneReturnedStatus",
    "WhereIsTheUnseenRazorStatus",
    "WindAndFreedomStatus",

    # Character Status
    "AdeptusTemptationStatus",
    "ButterCrabStatus",
    "FishAndChipsStatus",
    "FrozenStatus",
    "HeavyStrikeStatus",
    "JueyunGuobaStatus",
    "KingsSquireEffectStatus",
    "LithicGuardStatus",
    "LotusFlowerCrispStatus",
    "MintyMeatRollsStatus",
    "MoonpiercerEffectStatus",
    "MushroomPizzaStatus",
    "NorthernSmokedChickenStatus",
    "SashimiPlatterStatus",
    "SatiatedStatus",
    "TandooriRoastChickenStatus",
    "UnmovableMountainStatus",

    # character specific status
    ## Albedo ##
    "DescentOfDivinityStatus",
    ## Arataki Itto ##
    "AratakiIchibanStatus",
    "RagingOniKingStatus",
    "SuperlativeSuperstrengthStatus",
    ## Bennett ##
    "GrandExpectationStatus",
    "InspirationFieldStatus",
    "InspirationFieldEnhancedStatus",
    ## Chongyun ##
    "ChonghuasFrostFieldEnhancedStatus",
    "ChonghuasFrostFieldStatus",
    "SteadyBreathingStatus",
    ## Collei ##
    "ColleiTalentStatus",
    "FloralSidewinderStatus",
    "SproutStatus",
    ## Dehya ##
    "IncinerationDriveStatus",
    "StalwartAndTrueStatus",
    ## Diona ##
    "CatClawShieldEnhancedStatus",
    "CatClawShieldStatus",
    ## Electro Hypostasis ##
    "ElectroHypostasisPassiveStatus",
    "ElectroCrystalCoreStatus",
    "RockPaperScissorsComboPaperStatus",
    "RockPaperScissorsComboScissorsStatus",
    ## Eula ##
    "GrimheartStatus",
    "WellspingOfWarLustStatus",
    ## Fatui Cryo Cicin Mage ##
    "CicinsColdGlareStatus",
    "FlowingCicinShieldStatus",
    ## Fatui Pyro Agent ##
    "PaidInFullStatus",
    "StealthMasterStatus",
    "StealthStatus",
    ## Fischl ##
    "StellarPredatorStatus",
    ## Ganyu ##
    "GanyuTalentStatus",
    "IceLotusStatus",
    "UndividedHeartStatus",
    ## Hu Tao ##
    "BloodBlossomStatus",
    "ParamitaPapilioStatus",
    "SanguineRougeStatus",
    ## Jadeplume Terrorshroom ##
    "ProliferatingSporesStatus",
    "RadicalVitalityHiddenStatus",
    "RadicalVitalityStatus",
    ## Jean ##
    "LandsOfDandelionStatus",
    ## Kaedehara Kazuha ##
    "ChihayaburuStatus",
    "MidareRanzanStatus",
    "MidareRanzanCryoStatus",
    "MidareRanzanElectroStatus",
    "MidareRanzanHydroStatus",
    "MidareRanzanPyroStatus",
    "PoeticsOfFuubutsuStatus",
    "PoeticsOfFuubutsuCryoStatus",
    "PoeticsOfFuubutsuElectroStatus",
    "PoeticsOfFuubutsuHydroStatus",
    "PoeticsOfFuubutsuPyroStatus",
    ## Kaeya ##
    "ColdBloodedStrikeStatus",
    "IcicleStatus",
    ## Kamisato Ayaka ##
    "KamisatoArtSenhoStatus",
    "KamisatoAyakaCryoInfusionEnhancedStatus",
    "KamisatoAyakaCryoInfusionStatus",
    "KantenSenmyouBlessingStatus",
    ## Keqing ##
    "KeqingElectroInfusionEnhancedStatus",
    "KeqingElectroInfusionStatus",
    "KeqingTalentStatus",
    "ThunderingPenanceStatus",
    ## Klee ##
    "ExplosiveSparkStatus",
    "PoundingSurpriseStatus",
    "SparksnSplashStatus",
    ## Kujou Sara ##
    "CrowfeatherCoverStatus",
    "SinOfPrideStatus",
    ## Layla ##
    "CurtainOfSlumberStatus",
    "LightsRemitStatus",
    "ShootingStarStatus",
    ## Lisa ##
    "ConductiveStatus",
    "PulsatingWitchStatus",
    ## Lyney ##
    "ConclusiveOvationStatus",
    "PropSurplusStatus",
    ## Maguu Kenki ##
    "TranscendentAutomatonStatus",
    ## Mona ##
    "IllusoryBubbleStatus",
    "IllusoryTorrentStatus",
    "ProphecyOfSubmersionStatus",
    ## Nahida ##
    "SeedOfSkandhaStatus",
    "ShrineOfMayaStatus",
    "TheSeedOfStoredKnowledgeStatus",
    ## Ningguang ##
    "JadeScreenStatus",
    "StrategicReserveStatus",
    ## Noelle ##
    "FullPlateStatus",
    "IGotYourBackStatus",
    "SweepingTimeStatus",
    ## Qiqi ##
    "FortunePreservingTalismanStatus",
    "QiqiTalentStatus",
    "RiteOfResurrectionStatus",
    ## Raiden Shogun ##
    "ChakraDesiderataHiddenStatus",
    "ChakraDesiderataStatus",
    "WishesUnnumberedStatus",
    ## Rhodeia of Loch ##
    "StreamingSurgeStatus",
    ## Sangonomiya Kokomi ##
    "CeremonialGarmentStatus",
    "TamakushiCasketStatus",
    ## Shenhe ##
    "IcyQuillStatus",
    "MysticalAbandonStatus",
    ## Stonehide Lawachurl ##
    "StoneForceStatus",
    "StonehideReforgedStatus",
    "StonehideStatus",
    ## Tartaglia ##
    "AbyssalMayhemHydrospoutStatus",
    "MeleeStanceStatus",
    "RangeStanceStatus",
    "RiptideCounterStatus",
    "RiptideTransferStatus",
    "RiptideStatus",
    "TideWithholderStatus",
    ## Tighnari ##
    "KeenSightStatus",
    "VijnanaSuffusionStatus",
    ## Venti ##
    "EmbraceOfWindsStatus",
    "StormzoneStatus",
    "WindsOfHarmonyStatus",
    ## Wanderer##
    "DescentStatus",
    "GalesOfReverieStatus",
    "WindfavoredStatus",
    ## Xiangling ##
    "PyronadoStatus",
    ## Xingqiu ##
    "RainSwordStatus",
    "RainbowBladeworkStatus",
    "TheScentRemainedStatus",
    ## Yae Miko ##
    "RiteOfDispatchStatus",
    "TenkoThunderboltsStatus",
    "TheShrinesSacredShadeStatus",
    ## Yaoyao ##
    "AdeptalLegacyStatus",
    ## Yelan ##
    "BreakthroughStatus",
    "ExquisiteThrowStatus",
    "TurnControlStatus",
    "YelanPassiveStatus",
    ## Yoimiya ##
    "AurousBlazeStatus",
    "NaganoharaMeteorSwarmStatus",
    "NiwabiEnshouStatus",
]


############################## base ##############################
@dataclass(frozen=True)
class Status:
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset()
    """
    The set of signals the status may react to.
    This is used to improve the performance.
    """
    _AUTO_REUSE_SAME_UPDATE: ClassVar[bool] = True
    """ If `True`, then the status will reuse the same object if the update is equivalent. """

    def __init__(self) -> None:
        if type(self) is Status:  # pragma: no cover
            raise Exception("class Status is not instantiable")

    def preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        """
        :param game_state: the current game state.
        :param status_source: the position of this status.
        :param item: data to be preprocessed.
        :param signal: proprocessing signal.

        :returns: the preprocessed PreprocessableEvent and updated self.
                  If `None` is returned instead of a new self, then the status
                  is removed.
        """
        new_item, new_self = self._preprocess(game_state, status_source, item, signal)
        return self._post_preprocess(
            game_state,
            status_source,
            item,
            signal,
            new_item,
            new_self,
        )

    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        return item, self

    def _post_preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
            new_item: PreprocessableEvent,
            new_self: None | Self,
    ) -> tuple[PreprocessableEvent, None | Self]:
        return (new_item, new_self)

    def inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> GameState:
        """
        :param game_state: the current game state.
        :param status_source: the position of this status.
        :param info_type: the type of information.
        :param information: the information.

        :returns: the updated game state.
        """
        new_self = self._inform(game_state, status_source, info_type, information)
        if new_self == self:
            return game_state

        from ..summon import summon as sm
        from ..support import support as sp
        if isinstance(new_self, PersonalStatus):
            return eft.OverrideCharacterStatusEffect(
                target=status_source,
                status=new_self,
            ).execute(game_state)

        elif isinstance(new_self, PlayerHiddenStatus):
            return eft.OverrideHiddenStatusEffect(
                target_pid=status_source.pid,
                status=new_self,
            ).execute(game_state)

        elif isinstance(new_self, CombatStatus):
            return eft.OverrideCombatStatusEffect(
                target_pid=status_source.pid,
                status=new_self,
            ).execute(game_state)

        elif isinstance(new_self, sm.Summon):
            return eft.OverrideSummonEffect(
                target_pid=status_source.pid,
                summon=new_self,
            ).execute(game_state)

        elif isinstance(new_self, sp.Support):
            return eft.OverrideSupportEffect(
                target_pid=status_source.pid,
                support=new_self,
            ).execute(game_state)

        else:
            raise NotImplementedError

    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        return self

    _BUDGET_SIGNALS = frozenset({
        TriggeringSignal.POST_DMG,
        TriggeringSignal.DIRECT_TRIGGER,
    })

    def react_to_signal(
            self,
            game_state: GameState,
            source: StaticTarget,
            signal: TriggeringSignal,
            detail: None | InformableEvent = None,
    ) -> list[eft.Effect]:
        """
        :param game_state: the current game state.
        :param source: the status position in the game.
        :param signal: the triggering signal.
        :param silent: ignores some post checkers if `True`. (just leave it as `False`)

        :returns: a list of effects generated.
        """
        es, new_status = self._react_to_signal(game_state, source, signal, detail)
        es, new_status = self._post_react_to_signal(game_state, es, new_status, source, signal, detail)

        from ..summon import summon as sm
        from ..support import support as sp
        # do the removal or update of the status
        if isinstance(self, PersonalStatus):
            if new_status is None:
                es.append(eft.RemoveCharacterStatusEffect(
                    source,
                    type(self),
                ))
            elif new_status is not self and self.update(new_status) != self:  # type: ignore
                assert type(self) == type(new_status)
                es.append(eft.UpdateCharacterStatusEffect(
                    source,
                    new_status,  # type: ignore
                ))

        elif isinstance(self, PlayerHiddenStatus):
            if new_status is None:
                es.append(eft.RemoveHiddenStatusEffect(
                    source.pid,
                    type(self),
                ))
            elif new_status is not self and self.update(new_status) != self:  # type: ignore
                assert type(self) == type(new_status)
                es.append(eft.UpdateHiddenStatusEffect(
                    source.pid,
                    new_status,  # type: ignore
                ))

        elif isinstance(self, CombatStatus):
            if new_status is None:
                es.append(eft.RemoveCombatStatusEffect(
                    source.pid,
                    type(self),
                ))
            elif new_status is not self and self.update(new_status) != self:  # type: ignore
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
            elif new_status is not self and self.update(new_status) != self:  # type: ignore
                assert type(self) == type(new_status)
                es.append(eft.UpdateSummonEffect(
                    source.pid,
                    new_status,  # type: ignore
                ))

        elif isinstance(self, sp.Support):
            if new_status is None:
                es.append(eft.RemoveSupportEffect(
                    source.pid,
                    sid=self.sid,
                ))
            elif new_status is not self and self.update(new_status) != self:  # type: ignore
                assert type(self) == type(new_status)
                es.append(eft.UpdateSupportEffect(
                    source.pid,
                    new_status,  # type: ignore
                ))

        else:  # pragma: no cover
            raise NotImplementedError

        es = self._post_update_react_to_signal(game_state, es, source, signal, detail)

        has_damage = False
        for effect in es:
            has_damage = has_damage or isinstance(effect, eft.ReferredDamageEffect) \
                or isinstance(effect, eft.SpecificDamageEffect)

        if signal in self._BUDGET_SIGNALS:
            es += budget_post_effect(game_state, source.pid, has_damage)
        else:
            es += standard_post_effects(game_state, source.pid, has_damage)

        return es

    def _post_update_react_to_signal(
            self,
            game_state: GameState,
            effects: list[eft.Effect],
            source: StaticTarget,
            signal: TriggeringSignal,
            detail: None | InformableEvent,
    ) -> list[eft.Effect]:
        return effects

    def _post_react_to_signal(
            self, game_state: GameState, effects: list[eft.Effect], new_status: None | Self,
            source: StaticTarget, signal: TriggeringSignal, detail: None | InformableEvent,
    ) -> tuple[list[eft.Effect], None | Self]:
        if self._AUTO_REUSE_SAME_UPDATE:
            return effects, case_val(new_status == self, self, new_status)
        else:
            return effects, new_status

    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        """
        :param game_state: the current game state.
        :param source: the position of this status.
        :param signal: the triggering signal.
        :param detail: the detail of the signal if applicable.

        Returns a tuple, containg the effects and how to update self
        * if the returned new self is the same object as itself, then it is taken as no change
          requested
        * if the returned new self is none, then it is taken as a removal request
        * if the returned new self is different object than myself, then it is taken as an update
        """
        return [], self  # pragma: no cover

    def add(self, other: type[Self]) -> None | Self:
        """
        Defines how the status update itself with the addition of the same type.
        """
        return self.update(other())

    def update(self, other: Self) -> None | Self:
        """
        Defines how the status update itself with an incoming status of the same type.
        """
        new_self = self._update(other)
        return self._post_update(new_self)

    def _post_update(self, new_self: None | Self) -> None | Self:
        return new_self

    def _update(self, other: Self) -> None | Self:
        return other

    def _target_is_self_active(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            target: None | StaticTarget = None,
    ):
        """
        :param status_source: the positon of this status.
        :param target: the target to be checked, default to status_source if not provided.
        :returns: True if target is the active character of the player in ``game_state``.
        """
        if target is None:
            target = status_source
        return (
            status_source.pid is target.pid
            and target.zone is Zone.CHARACTERS
            and status_source.id == game_state.get_player(
                status_source.pid
            ).characters.get_active_character_id()
        )

    def _some_char_equiped_talent(
            self, game_state: GameState, pid: Pid, char_type: type[Character],
    ) -> bool:
        alive_chars = game_state.get_player(pid).characters.get_alive_characters()
        return any(
            char.talent_equipped()
            for char in alive_chars
            if isinstance(char, char_type)
        )

    def _player_can_plunge(self, game_state: GameState, pid: Pid) -> bool:
        return game_state.get_player(pid).hidden_statuses.just_find(PlungeAttackStatus).can_plunge

    def perspective_view(self) -> Self:
        """
        Returns the self in the eyes of the opponent, hiding relevant information.
        """
        return self

    @classmethod
    def has_perspective_view(cls) -> bool:
        """
        Returns True if the status has a perspective view.
        """
        return cls.perspective_view is not Status.perspective_view

    def encoding(self, encoding_plan: EncodingPlan) -> list[int]:
        """
        :returns: the encoding of the content of the status. (excluding the type of status)
        """
        field_names = set(field.name for field in fields(self))
        usages_value = self.__getattribute__("usages") if "usages" in field_names else 0
        field_names.discard("usages")
        values = [usages_value] + list(chain(*[
            [self.__getattribute__(field_name)]
            for field_name in field_names
        ]))
        ret_val = [encoding_plan.encode_item(self)]
        for value in values:
            if isinstance(value, bool):
                ret_val.append(1 if value else 0)
            elif isinstance(value, int):
                ret_val.append(value)
            elif isinstance(value, Enum):
                assert isinstance(value.value, int), value
                ret_val.append(encoding_plan.encode_item(value))
            elif value is None:
                ret_val.append(0)
            else:
                raise Exception(f"unknown type {type(value)} from {self}")
        fillings = encoding_plan.STATUS_FIXED_LEN - len(ret_val)
        if fillings < 0:
            raise Exception(f"status {self} has too many fields")
        for _ in range(fillings):
            ret_val.append(0)
        return ret_val

    def __str__(self) -> str:
        return self.__class__.__name__.removesuffix("Status")  # pragma: no cover


############################## type ##############################

@dataclass(frozen=True)
class PlayerHiddenStatus(Status):
    pass


@dataclass(frozen=True)
class PersonalStatus(Status):
    def talent_equiped(self, game_state: GameState, status_source: StaticTarget) -> bool:
        char = game_state.get_character_target(status_source)
        assert char is not None
        return char.talent_equipped()


@dataclass(frozen=True)
class CharacterHiddenStatus(PersonalStatus):
    """
    Basic status, describing character talents
    """
    pass


@dataclass(frozen=True)
class EquipmentStatus(PersonalStatus):
    """
    Basic status, describing weapon, artifact and character unique talents
    """
    @cached_classproperty
    def CARD(cls) -> type[crd.EquipmentCard]:
        raise NotImplementedError()


@dataclass(frozen=True)
class TalentEquipmentStatus(EquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.EquipmentCard]:
        raise NotImplementedError()


@dataclass(frozen=True)
class WeaponEquipmentStatus(EquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType]

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        raise NotImplementedError()

    BASE_DAMAGE_BOOST: ClassVar[int] = 1

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
            if (
                dmg.source == status_source
                and dmg.damage_type.directly_from_character()
                and dmg.element is not Element.PIERCING
            ):
                return self._process_dmg(game_state, status_source, item)
        return super()._preprocess(game_state, status_source, item, signal)

    def _process_dmg(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            dmg: DmgPEvent,
    ) -> tuple[DmgPEvent, Self]:
        return dmg.delta_damage(self.BASE_DAMAGE_BOOST), self


@dataclass(frozen=True)
class ArtifactEquipmentStatus(EquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        raise NotImplementedError(cls)


@dataclass(frozen=True)
class CharacterStatus(PersonalStatus):
    """
    Basic status, private status to each character
    """
    pass


@dataclass(frozen=True)
class CombatStatus(Status):
    """
    Basic status, status shared across the team
    """

    @override
    def _target_is_self_active(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            target: None | StaticTarget = None,
    ) -> bool:
        """ target needs to be not None """
        assert target is not None
        active_char = game_state.get_player(status_source.pid).get_active_character()
        if active_char is None:
            return False
        return StaticTarget(
            pid=status_source.pid,
            zone=Zone.CHARACTERS,
            id=active_char.id,
        ) == target


############################## template ##############################
@dataclass(frozen=True)
class _UsageStatus(Status):
    """
    A Status template that provides auto handling of usages.

    - for ._react_to_signal(), returning same self means no change, otherwise, the returned
      usages will be treated as delta usages.
    - for ._preprocess() and ._inform(), the returned usages will be the final usages.
    """
    #: default usages on creation
    usages: int
    #: maximum usages
    MAX_USAGES: ClassVar[int] = BIG_INT
    #: usages added when recreated
    REPEATED_USAGES: ClassVar[int | None] = None
    AUTO_DESTROY: ClassVar[bool] = True

    _AUTO_REUSE_SAME_UPDATE: ClassVar[bool] = False

    @override
    def _post_preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
            new_item: PreprocessableEvent,
            new_self: None | Self,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if new_self is not None:
            if self.AUTO_DESTROY and new_self.usages <= 0:
                new_self = None
            elif new_self.usages < 0:
                new_self = replace(new_self, usages=0)
        return super()._post_preprocess(game_state, status_source, item, signal, new_item, new_self)

    @override
    def _post_update(self, new_self: None | Self) -> None | Self:
        """ remove the status if usages <= 0 """
        if new_self is not None:
            if self.AUTO_DESTROY and new_self.usages <= 0:
                new_self = None
            elif new_self.usages < 0:
                new_self = replace(new_self, usages=0)
        return super()._post_update(new_self)

    @override
    def _update(self, other: Self) -> None | Self:
        max_usages = max((self.usages, other.usages, self.MAX_USAGES))
        new_usages = min(self.usages + other.usages, max_usages)
        return replace(other, usages=new_usages)

    @override
    def add(self, other: type[Self]) -> None | Self:
        if self.REPEATED_USAGES is None:
            return super().add(other)
        return self.update(other(usages=self.REPEATED_USAGES))

    def __str__(self) -> str:
        return super().__str__() + f"({self.usages})"  # pragma: no cover


class _UsageLivingStatus(_UsageStatus):
    """ Same as _UsageStatus, but does not auto destroy itself when usages is 0 or below. """
    AUTO_DESTROY: ClassVar[bool] = False


@dataclass(frozen=True)
class _ShieldStatus(Status):
    def _is_target(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: eft.SpecificDamageEffect,
    ) -> bool:
        from ..summon import summon as sm
        if isinstance(self, PersonalStatus):
            return item.target == status_source

        elif isinstance(self, CombatStatus):
            attached_active_character = StaticTarget(
                status_source.pid,
                zone=Zone.CHARACTERS,
                id=game_state.get_player(status_source.pid).just_get_active_character().id,
            )
            return item.target == attached_active_character

        elif isinstance(self, sm.Summon):
            attached_active_character = StaticTarget(
                status_source.pid,
                zone=Zone.CHARACTERS,
                id=game_state.get_player(status_source.pid).just_get_active_character().id,
            )
            return item.target == attached_active_character

        else:
            raise NotImplementedError  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class FixedShieldStatus(_ShieldStatus, _UsageStatus):
    """
    The shield status where only one usage can be consumed by a DMG effect.
    Typically appeared to be violet in game.
    """
    usages: int
    MAX_USAGES: ClassVar[int] = BIG_INT
    SHIELD_AMOUNT: ClassVar[int] = 0  # shield amount per stack

    def _triggering_condition(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            damage: eft.SpecificDamageEffect
    ) -> bool:
        return True

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
            if dmg.damage > 0 and self.usages > 0 \
                    and dmg.element != Element.PIERCING \
                    and self._is_target(game_state, status_source, dmg) \
                    and self._triggering_condition(game_state, status_source, dmg):
                new_dmg_amount = max(0, dmg.damage - self.SHIELD_AMOUNT)
                new_dmg = replace(dmg, damage=new_dmg_amount)
                new_item = DmgPEvent(dmg=new_dmg)
                new_usages = self.usages - 1
                if self.AUTO_DESTROY and new_usages == 0:
                    return new_item, None
                else:
                    return new_item, replace(self, usages=new_usages)

        return super()._preprocess(game_state, status_source, item, signal)


@dataclass(frozen=True, kw_only=True)
class StackedShieldStatus(_ShieldStatus, _UsageStatus):
    """
    The shield status where all usages can be consumed by a DMG effect.
    Typically appeared to be yellow in game.
    """
    usages: int
    MAX_USAGES: ClassVar[int] = BIG_INT
    SHIELD_AMOUNT: ClassVar[int] = 1  # shield amount per usage

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
            if dmg.damage > 0 and self.usages > 0 \
                    and dmg.element != Element.PIERCING \
                    and self._is_target(game_state, status_source, dmg):
                usages_consumed = min(ceil(dmg.damage / self.SHIELD_AMOUNT), self.usages)
                new_dmg_amount = max(0, dmg.damage - usages_consumed * self.SHIELD_AMOUNT)
                new_dmg = replace(dmg, damage=new_dmg_amount)
                new_item = DmgPEvent(dmg=new_dmg)
                new_usages = self.usages - usages_consumed
                if new_usages == 0:
                    return new_item, None
                else:
                    return new_item, replace(self, usages=new_usages)

        return super()._preprocess(game_state, status_source, item, signal)

    def __str__(self) -> str:
        return super().__str__() + f"({self.usages})"  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class PrepareSkillStatus(Status):
    pass


@dataclass(frozen=True, kw_only=True)
class RevivalStatus(Status):
    @abstractmethod
    def revivable(
            self, game_state: GameState, status_source: StaticTarget, char_source: StaticTarget,
    ) -> bool:
        pass


@dataclass(frozen=True, kw_only=True)
class _InfusionStatus(_UsageStatus):
    MAX_USAGES: ClassVar[int] = BIG_INT
    ELEMENT: ClassVar[Element]
    DAMAGE_BOOST: ClassVar[int] = 0
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
        new_item: None | DmgPEvent = None
        if isinstance(item, DmgPEvent):
            dmg = item.dmg
            if signal is Preprocessables.DMG_ELEMENT:
                if self._dmg_element_condition(game_state, status_source, dmg):
                    new_item = replace(item, dmg=replace(dmg, element=self.ELEMENT))
            if signal is Preprocessables.DMG_AMOUNT_PLUS:
                if self.DAMAGE_BOOST != 0  \
                        and self._dmg_boost_condition(game_state, status_source, dmg):
                    new_item = replace(item, dmg=replace(
                        dmg, damage=dmg.damage + self.DAMAGE_BOOST))
        if new_item is not None:
            return new_item, self
        else:
            return item, self

    def _dmg_element_condition(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: eft.SpecificDamageEffect,
    ) -> bool:
        return item.element is Element.PHYSICAL \
            and item.damage_type.direct_normal_attack() \
            and self._target_is_self_active(game_state, status_source, item.source)

    def _dmg_boost_condition(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: eft.SpecificDamageEffect,
    ) -> bool:
        return (
            item.element is self.ELEMENT
            and item.damage_type.directly_from_character()
            and self._target_is_self_active(game_state, status_source, item.source)
        )

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        d_usages = 0
        if signal is TriggeringSignal.ROUND_END:
            d_usages = -1
        return [], replace(self, usages=d_usages)


@dataclass(frozen=True, kw_only=True)
class _SkillCostReductionStatus(Status):
    COST_DEDUCTION: ClassVar[int] = 2
    DISCOUNTED_SKILL_TYPES: ClassVar[frozenset[CharacterSkillType]] = frozenset((
        CharacterSkillType.ELEMENTAL_SKILL,
    ))
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
        if signal is Preprocessables.SKILL_COST_OMNI:
            assert isinstance(item, ActionPEvent)
            if (
                    item.source == status_source
                    and item.event_sub_type in self.DISCOUNTED_SKILL_TYPES
                    and item.dice_cost.can_cost_less_elem()
            ):
                new_cost = item.dice_cost.cost_less_elem(self.COST_DEDUCTION)
                return replace(item, dice_cost=new_cost), None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover

############################## Hidden Status ##############################


@dataclass(frozen=True, kw_only=True)
class ArcaneLegendUsedStatus(PlayerHiddenStatus):
    pass


@dataclass(frozen=True, kw_only=True)
class ChargedAttackStatus(PlayerHiddenStatus):
    """
    When present, character's normal attack of the player should be treated as charged-attack
    """
    can_charge: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.can_charge:
            return [], replace(self, can_charge=False)
        return [], self


@dataclass(frozen=True, kw_only=True)
class PlungeAttackStatus(PlayerHiddenStatus):
    can_plunge: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.ROUND_END,
        TriggeringSignal.SELF_SWAP,
    ))

    # @override
    # def _inform(
    #         self,
    #         game_state: GameState,
    #         status_source: StaticTarget,
    #         info_type: Informables,
    #         information: InformableEvent,
    # ) -> Self:
    #     if info_type is Informables.SKILL_USAGE:
    #         assert isinstance(information, SkillIEvent)
    #         if information.source == status_source \
    #                 and self.can_plunge:
    #             return replace(self, can_plunge=False)
    #     return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.can_plunge:
            return [], replace(self, can_plunge=False)
        elif signal is TriggeringSignal.ROUND_END and self.can_plunge:
            return [], replace(self, can_plunge=False)
        elif signal is TriggeringSignal.SELF_SWAP:
            if not self.can_plunge:
                return [], replace(self, can_plunge=True)
        return [], self

    @override
    def __str__(self) -> str:
        return super().__str__() + f"({case_val(self.can_plunge, '*', '')})"


@dataclass(frozen=True, kw_only=True)
class DeathThisRoundStatus(PlayerHiddenStatus):
    activated: bool = False

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.CHARACTER_DEATH:
            assert isinstance(information, CharacterDeathIEvent)
            if not self.activated and information.target.pid == status_source.pid:
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            if self.activated:
                return [], replace(self, activated=False)
        return [], self

    def __str__(self) -> str:
        return super().__str__() + f"({case_val(self.activated, '*', '')})"

############################## Equipment Status ##############################

########## Weapon Status ##########


@dataclass(frozen=True, kw_only=True)
class _SacrificialWeaponStatus(WeaponEquipmentStatus, _UsageLivingStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    activated: bool = False
    DICE_GAIN_NUM: ClassVar[int] = 1

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.ROUND_END,
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
            if (
                    self.usages > 0
                    and information.skill_true_type is CharacterSkillType.ELEMENTAL_SKILL
                    and information.source == status_source
            ):
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL:
            if self.activated:
                assert self.usages > 0
                equiper = game_state.get_character_target(source)
                assert equiper is not None
                return [
                    eft.AddDiceEffect(
                        source=source.with_status(type(self)),
                        pid=source.pid,
                        element=equiper.ELEMENT,
                        num=self.DICE_GAIN_NUM,
                    )
                ], replace(self, activated=False, usages=-1)
        elif signal is TriggeringSignal.ROUND_END:
            if self.usages < self.MAX_USAGES:
                return [], replace(self, usages=self.MAX_USAGES)
        return [], self

#### Bow ####


@dataclass(frozen=True, kw_only=True)
class AmosBowStatus(WeaponEquipmentStatus, _UsageLivingStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.BOW
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    activated: bool = False
    ADDITIONAL_DMG_BOOST: ClassVar[int] = 2

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import AmosBow
        return AmosBow

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.PRE_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if not (
                    self.usages > 0
                    and self._target_is_self_active(game_state, status_source, information.source)
            ):
                return self
            this_char = game_state.get_character_target(status_source)
            assert this_char is not None
            total_cost = (
                this_char.skill_cost(information.skill_type).num_dice()
                + this_char.skill_energy_cost(information.skill_type)
            )
            if total_cost < 5:
                return self
            return replace(self, activated=True)
        if info_type is Informables.POST_SKILL_USAGE and self.activated:
            return replace(self, activated=False)
        return self

    @override
    def _process_dmg(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            dmg: DmgPEvent,
    ) -> tuple[DmgPEvent, Self]:
        delta_dmg = self.BASE_DAMAGE_BOOST
        if not self.activated:
            return dmg.delta_damage(delta_dmg), self
        assert self.usages > 0
        delta_dmg += self.ADDITIONAL_DMG_BOOST
        return dmg.delta_damage(delta_dmg), replace(self, usages=self.usages - 1, activated=False)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


@dataclass(frozen=True, kw_only=True)
class ElegyForTheEndStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.BOW
    activated: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import ElegyForTheEnd
        return ElegyForTheEnd

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if (
                not self.activated
                and isinstance(information, SkillIEvent)
                and information.source == status_source
                and information.skill_true_type.is_elemental_burst()
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
                eft.AddCombatStatusEffect(
                    target_pid=source.pid,
                    status=MillennialMovementFarewellSongStatus,
                ),
            ], replace(self, activated=False)
        return [], self


@dataclass(frozen=True, kw_only=True)
class KingsSquireStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.BOW

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import KingsSquire
        return KingsSquire


@dataclass(frozen=True, kw_only=True)
class RavenBowStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.BOW

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import RavenBow
        return RavenBow


@dataclass(frozen=True, kw_only=True)
class SacrificialBowStatus(_SacrificialWeaponStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.BOW

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import SacrificialBow
        return SacrificialBow

#### Catalyst ####


@dataclass(frozen=True, kw_only=True)
class AThousandFloatingDreamsStatus(WeaponEquipmentStatus, _UsageLivingStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.CATALYST
    DMG_BOOST: ClassVar[int] = 1
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import AThousandFloatingDreams
        return AThousandFloatingDreams

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        item, new_self = super()._preprocess(game_state, status_source, item, signal)
        if new_self is None:
            return item, new_self
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                    new_self.usages > 0
                    and dmg.source.pid is status_source.pid
                    and dmg.damage_type.directly_from_character()
                    and dmg.reaction is not None
            ):
                return (
                    item.delta_damage(new_self.DMG_BOOST),
                    replace(new_self, usages=new_self.usages - 1),
                )
        return item, new_self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class FruitOfFulfillmentStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.CATALYST

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import FruitOfFulfillment
        return FruitOfFulfillment


@dataclass(frozen=True, kw_only=True)
class MagicGuideStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.CATALYST

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import MagicGuide
        return MagicGuide


@dataclass(frozen=True, kw_only=True)
class SacrificialFragmentsStatus(_SacrificialWeaponStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.CATALYST

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import SacrificialFragments
        return SacrificialFragments

#### Claymore ####


@dataclass(frozen=True, kw_only=True)
class SacrificialGreatswordStatus(_SacrificialWeaponStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.CLAYMORE

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import SacrificialGreatsword
        return SacrificialGreatsword


@dataclass(frozen=True, kw_only=True)
class TheBellStatus(WeaponEquipmentStatus, _UsageLivingStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.CLAYMORE
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    activated: bool = False

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.ROUND_END,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import TheBell
        return TheBell

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
            if (
                    self.usages > 0
                    and not self.activated
                    and information.source == status_source
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
                eft.AddCombatStatusEffect(
                    target_pid=source.pid,
                    status=RebelliousShieldStatus,
                ),
            ], replace(self, usages=-1, activated=False)
        elif signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            assert not self.activated
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


@dataclass(frozen=True, kw_only=True)
class WhiteIronGreatswordStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.CLAYMORE

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import WhiteIronGreatsword
        return WhiteIronGreatsword


@dataclass(frozen=True, kw_only=True)
class WolfsGravestoneStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.CLAYMORE
    HP_THRESHOLD: ClassVar[int] = 6
    ADDITIONAL_DMG_BOOST: ClassVar[int] = 2

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import WolfsGravestone
        return WolfsGravestone

    @override
    def _process_dmg(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            dmg: DmgPEvent,
    ) -> tuple[DmgPEvent, Self]:
        oppo_active_char = game_state.get_player(
            status_source.pid.other
        ).just_get_active_character()
        final_dmg_boost = self.BASE_DAMAGE_BOOST
        if oppo_active_char.hp <= self.HP_THRESHOLD:
            final_dmg_boost += self.ADDITIONAL_DMG_BOOST
        return dmg.delta_damage(final_dmg_boost), self


#### Polearm ####

@dataclass(frozen=True, kw_only=True)
class EngulfingLightningStatus(WeaponEquipmentStatus, _UsageLivingStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.POLEARM
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_START,
        TriggeringSignal.POST_ANY,
        TriggeringSignal.ROUND_END,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import EngulfingLightning
        return EngulfingLightning

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if (
                (
                    signal is TriggeringSignal.ROUND_START
                    or signal is TriggeringSignal.POST_ANY
                )
                and self.usages > 0
        ):
            attached_char = game_state.get_character_target(source)
            assert attached_char is not None
            if attached_char.energy == 0:
                return [
                    eft.EnergyRechargeEffect(
                        target=source,
                        amount=1,
                    ),
                ], replace(self, usages=-1)
        elif signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


@dataclass(frozen=True, kw_only=True)
class LithicSpearStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.POLEARM

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import LithicSpear
        return LithicSpear


@dataclass(frozen=True, kw_only=True)
class MoonpiercerStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.POLEARM

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import Moonpiercer
        return Moonpiercer


@dataclass(frozen=True, kw_only=True)
class VortexVanquisherStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.POLEARM
    ADDITIONAL_DMG_BOOST: ClassVar[int] = 1

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import VortexVanquisher
        return VortexVanquisher

    @override
    def _process_dmg(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            dmg: DmgPEvent,
    ) -> tuple[DmgPEvent, Self]:
        this_player = game_state.get_player(status_source.pid)
        active_char = this_player.just_get_active_character()
        final_dmg_boost = self.BASE_DAMAGE_BOOST
        if (
                any(
                    isinstance(status, StackedShieldStatus)
                    for status in this_player.combat_statuses
                )
                or any(
                    isinstance(status, StackedShieldStatus)
                    for status in active_char.character_statuses
        )
        ):
            final_dmg_boost += self.ADDITIONAL_DMG_BOOST
        return dmg.delta_damage(final_dmg_boost), self


@dataclass(frozen=True, kw_only=True)
class WhiteTasselStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.POLEARM

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import WhiteTassel
        return WhiteTassel

#### Sword ####


@dataclass(frozen=True, kw_only=True)
class AquilaFavoniaStatus(WeaponEquipmentStatus, _UsageLivingStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.SWORD
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    activated: bool = False
    HP_RECOVERY: ClassVar[int] = 1

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.ROUND_END,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import AquilaFavonia
        return AquilaFavonia

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
            if (
                    self.usages > 0
                    and not self.activated
                    and information.source.pid is status_source.pid.other
            ):
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.activated:
            if self._target_is_self_active(game_state, source, source):
                return [
                    eft.RecoverHPEffect(
                        source=source,
                        target=source,
                        recovery=self.HP_RECOVERY,
                    ),
                ], replace(self, usages=-1, activated=False)
            else:
                return [], replace(self, usages=0, activated=False)
        elif signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class FavoniusSwordStatus(WeaponEquipmentStatus, _UsageLivingStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.SWORD
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    activated: bool = False
    ENERGY_RECHARGE_AMOUNT: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.ROUND_END,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import FavoniusSword
        return FavoniusSword

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
            if (
                    self.usages > 0
                    and not self.activated
                    and information.source == status_source
                    and information.skill_true_type is CharacterSkillType.ELEMENTAL_SKILL
            ):
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.activated:
            attached_char = game_state.get_character_target(source)
            assert attached_char is not None
            if attached_char.energy < attached_char.max_energy:
                return [
                    eft.EnergyRechargeEffect(
                        target=source,
                        amount=self.ENERGY_RECHARGE_AMOUNT,
                    ),
                ], replace(self, usages=-1, activated=False)
            else:
                return [], replace(self, usages=0, activated=False)
        elif signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class SacrificialSwordStatus(_SacrificialWeaponStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.SWORD

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import SacrificialSword
        return SacrificialSword


@dataclass(frozen=True, kw_only=True)
class TravelersHandySwordStatus(WeaponEquipmentStatus):
    WEAPON_TYPE: ClassVar[WeaponType] = WeaponType.SWORD

    @cached_classproperty
    def CARD(cls) -> type[crd.WeaponEquipmentCard]:
        from ..card.card import TravelersHandySword
        return TravelersHandySword


########## Artifact Status ##########


@dataclass(frozen=True, kw_only=True)
class _ElementalDiscountStatus(ArtifactEquipmentStatus):
    """
    The template for budget elemental artifacts.
    """
    available: bool = True
    _ELEMENT: ClassVar[Element]
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        """
        If this "status_source" casts a skill or talent card is played on "status_source",
        the elemental cost of the card is reduced by 1.
        """
        if signal is Preprocessables.CARD1_COST_ELEM:
            assert isinstance(item, CardPEvent)
            from ..card.card import TalentCard
            if (
                    item.pid is status_source.pid
                    and self.available
                    and issubclass(item.card_type, TalentCard)
                    and item.dice_cost.can_cost_less_elem(self._ELEMENT)
                    and (target := item.card_type.implicit_target(game_state, item.pid)) is not None
                    and target == status_source
            ):
                new_cost = item.dice_cost.cost_less_elem(1, self._ELEMENT)
                return item.with_new_cost(new_cost), replace(self, available=False)
        elif signal is Preprocessables.SKILL_COST_ELEM:
            assert isinstance(item, ActionPEvent)
            if (
                    item.source == status_source
                    and self.available
                    and item.event_type.is_skill()
                    and item.dice_cost.can_cost_less_elem(self._ELEMENT)
            ):
                new_cost = item.dice_cost.cost_less_elem(1, self._ELEMENT)
                return replace(item, dice_cost=new_cost), replace(self, available=False)
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END and not self.available:
            return [], replace(self, available=True)
        return [], self


class _ElementalDiscountSupplyStatus(_ElementalDiscountStatus):
    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.ROLL_DICE_INIT:
            assert isinstance(item, DiceRollInitPEvent)
            if (
                    item.pid == status_source.pid
                    and item.can_update()
            ):
                return item.update(self._ELEMENT, 2), self
        return super()._preprocess(game_state, status_source, item, signal)


@dataclass(frozen=True, kw_only=True)
class ArchaicPetraStatus(_ElementalDiscountSupplyStatus):
    _ELEMENT: ClassVar[Element] = Element.GEO

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import ArchaicPetra
        return ArchaicPetra

@dataclass(frozen=True, kw_only=True)
class BlizzardStrayerStatus(_ElementalDiscountSupplyStatus):
    _ELEMENT: ClassVar[Element] = Element.CRYO

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import BlizzardStrayer
        return BlizzardStrayer

@dataclass(frozen=True, kw_only=True)
class BrokenRimesEchoStatus(_ElementalDiscountStatus):
    _ELEMENT: ClassVar[Element] = Element.CRYO

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import BrokenRimesEcho
        return BrokenRimesEcho


@dataclass(frozen=True, kw_only=True)
class CrimsonWitchOfFlamesStatus(_ElementalDiscountSupplyStatus):
    _ELEMENT: ClassVar[Element] = Element.PYRO

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import CrimsonWitchOfFlames
        return CrimsonWitchOfFlames


@dataclass(frozen=True, kw_only=True)
class _CrownOfWatatsumiStatus(ArtifactEquipmentStatus, _UsageLivingStatus):
    usages: int = 0
    MAX_USAGES: ClassVar[int] = 2
    accumulated_healing: int = 0
    HEALING_THRESHOLD: ClassVar[int] = 3
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_HEALING,
    ))

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            if not (
                    self.usages > 0
                    and item.dmg.source == status_source
                    and item.dmg.damage_type.directly_from_character()
            ):
                return item, self
            return item.delta_damage(self.usages), replace(self, usages=0)
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_HEALING:
            assert isinstance(detail, HealingIEvent)
            if not (
                    self.usages < self.MAX_USAGES
                    and detail.target.pid == source.pid
            ):
                return [], self
            new_acc_healing = self.accumulated_healing + detail.healing
            if new_acc_healing < self.HEALING_THRESHOLD:
                return [], replace(self, usages=0, accumulated_healing=new_acc_healing)
            d_usages = min(new_acc_healing // self.HEALING_THRESHOLD, self.MAX_USAGES - self.usages)
            new_acc_healing = (
                new_acc_healing % self.HEALING_THRESHOLD
                if d_usages + self.usages < self.MAX_USAGES
                else 0
            )
            return [], replace(self, usages=d_usages, accumulated_healing=new_acc_healing)
        return [], self


@dataclass(frozen=True, kw_only=True)
class CrownOfWatatsumiStatus(_CrownOfWatatsumiStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import CrownOfWatatsumi
        return CrownOfWatatsumi


@dataclass(frozen=True, kw_only=True)
class DeepwoodMemoriesStatus(_ElementalDiscountSupplyStatus):
    _ELEMENT: ClassVar[Element] = Element.DENDRO

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import DeepwoodMemories
        return DeepwoodMemories


@dataclass(frozen=True, kw_only=True)
class EchoesOfAnOfferingStatus(ArtifactEquipmentStatus):
    normal_attack_effect: bool = True
    skill_effect: bool = True
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.ROUND_END,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import EchoesOfAnOffering
        return EchoesOfAnOffering

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL:
            assert isinstance(detail, SkillIEvent)
            if detail.source != source or not (self.normal_attack_effect or self.skill_effect):
                return [], self
            player = game_state.get_player(source.pid)
            effects: list[eft.Effect] = []
            new_self = self
            if self.skill_effect and player.dice.num_dice() <= player.hand_cards.num_cards():
                effects.append(eft.AddDiceEffect(
                    source=source.with_status(type(self)),
                    pid=source.pid,
                    element=player.characters.just_get_character(cast(int, source.id)).ELEMENT,
                    num=1,
                ))
                new_self = replace(new_self, skill_effect=False)
            if self.normal_attack_effect and detail.skill_true_type.is_normal_attack():
                if self.skill_effect and not new_self.skill_effect:
                    effects.append(eft.EffectsGroupEndEffect())
                effects.append(eft.DrawTopCardEffect(
                    pid=source.pid,
                    num=1,
                ))
                new_self = replace(new_self, normal_attack_effect=False)
            return effects, new_self
        elif signal is TriggeringSignal.ROUND_END and not (self.normal_attack_effect and self.skill_effect):
            return [], type(self)()
        return [], self

    def __str__(self) -> str:
        return super().__str__() + f"({'O' if self.normal_attack_effect else 'X'}{'O' if self.skill_effect else 'X'})"


@dataclass(frozen=True, kw_only=True)
class ExilesCircletStatus(ArtifactEquipmentStatus, _UsageLivingStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.ROUND_END,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.ExilesCirclet]:
        from ..card.card import ExilesCirclet
        return ExilesCirclet

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.usages > 0:
            assert isinstance(detail, SkillIEvent)
            if (
                    detail.source == source
                    and detail.skill_type.is_elemental_burst()
            ):
                return [
                    eft.EnergyRechargeEffect(
                        target=StaticTarget.from_char_id(source.pid, char.id),
                        amount=1,
                    )
                    for char in game_state.get_player(source.pid).characters.get_required_chars(
                        activity_order=True, alive=True, non_active=True,
                    )
                ], replace(self, usages=-1) 
        elif signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES: 
            return [], type(self)()
        return [], self


@dataclass(frozen=True, kw_only=True)
class _OrnateKabutoStatus(ArtifactEquipmentStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL:
            assert isinstance(detail, SkillIEvent)
            if (
                    detail.source.pid is source.pid
                    and detail.source.id != source.id
                    and detail.skill_type.is_elemental_burst()
            ):
                return [eft.EnergyRechargeEffect(
                    target=source,
                    amount=1,
                )], self
        return [], self


@dataclass(frozen=True, kw_only=True)
class EmblemOfSeveredFateStatus(_OrnateKabutoStatus):
    DMG_BOOST: ClassVar[int] = 2

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import EmblemOfSeveredFate
        return EmblemOfSeveredFate

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            if (
                    item.dmg.source == status_source
                    and item.dmg.damage_type.direct_elemental_burst()
            ):
                return item.delta_damage(self.DMG_BOOST), self
        return item, self


@dataclass(frozen=True, kw_only=True)
class FlowingRingsStatus(ArtifactEquipmentStatus, _UsageLivingStatus):
    usages: int = 1
    activated: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.ROUND_END,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import FlowingRings
        return FlowingRings

    @override
    def _inform(
            self, game_state: GameState, status_source: StaticTarget, info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if (
                    information.source == status_source
                    and information.skill_true_type.is_normal_attack()
                    and not self.activated
                    and self.usages > 0
            ):
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.activated:
            assert self.usages > 0
            return [
                eft.DrawTopCardEffect(pid=source.pid, num=1),
            ], replace(self, usages=-1, activated=False)
        elif signal is TriggeringSignal.ROUND_END and self.usages < 1:
            assert not self.activated
            return [], replace(self, usages=1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class GamblersEarringsStatus(ArtifactEquipmentStatus, _UsageLivingStatus):
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 3
    DICE_GEN_NUM: ClassVar[int] = 2

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_DMG,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import GamblersEarrings
        return GamblersEarrings

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_DMG:
            assert isinstance(detail, DmgIEvent)
            if (
                    self.usages > 0
                    and detail.lethal
                    and detail.dmg.target.pid is not source.pid
                    and self._target_is_self_active(game_state, source)
            ):
                return [
                    eft.AddDiceEffect(
                        source=source.with_status(type(self)),
                        pid=source.pid,
                        element=Element.OMNI,
                        num=self.DICE_GEN_NUM,
                    ),
                ], replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class GeneralsAncientHelmStatus(ArtifactEquipmentStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_START,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import GeneralsAncientHelm
        return GeneralsAncientHelm

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_START:
            return [
                eft.AddCharacterStatusEffect(
                    target=source,
                    status=UnmovableMountainStatus,
                ),
            ], self
        return [], self


@dataclass(frozen=True, kw_only=True)
class _ShadowOfTheSandKingLikeStatus(ArtifactEquipmentStatus, _UsageLivingStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_DMG,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_DMG:
            assert isinstance(detail, DmgIEvent)
            if (
                    self.usages > 0
                    and self._target_is_self_active(game_state, source)
                    and detail.dmg.target.pid is source.pid.other
                    and detail.dmg.reaction is not None
            ):
                return [
                    eft.DrawTopCardEffect(pid=source.pid, num=1),
                ], replace(self, usages=-1)
        elif signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


@dataclass(frozen=True, kw_only=True)
class GildedDreamsStatus(_ShadowOfTheSandKingLikeStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import GildedDreams
        return GildedDreams


@dataclass(frozen=True, kw_only=True)
class _HeartOfKhvarenasBrillianceLikeStatus(ArtifactEquipmentStatus, _UsageLivingStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_DMG,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_DMG:
            assert isinstance(detail, DmgIEvent)
            if not (
                    self._target_is_self_active(game_state, source, source)
                    and self.usages > 0
                    and detail.dmg.target == source
            ):
                return [], self
            return [
                eft.DrawTopCardEffect(pid=source.pid, num=1),
            ], replace(self, usages=-1)
        elif signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


@dataclass(frozen=True, kw_only=True)
class HeartOfDepthStatus(_ElementalDiscountSupplyStatus):
    _ELEMENT: ClassVar[Element] = Element.HYDRO

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import HeartOfDepth
        return HeartOfDepth


@dataclass(frozen=True, kw_only=True)
class HeartOfKhvarenasBrillianceStatus(_HeartOfKhvarenasBrillianceLikeStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import HeartOfKhvarenasBrilliance
        return HeartOfKhvarenasBrilliance


@dataclass(frozen=True, kw_only=True)
class InstructorsCapStatus(ArtifactEquipmentStatus, _UsageLivingStatus):
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 3
    activated: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.ROUND_END,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import InstructorsCap
        return InstructorsCap

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.REACTION_TRIGGERED:
            assert isinstance(information, ReactionIEvent)
            if (
                    not self.activated
                    and self.usages > 0
                    and information.source == status_source
                    and information.source_type.directly_from_character()
            ):
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.activated:
            this_char = game_state.get_character_target(source)
            assert this_char is not None
            return [
                eft.AddDiceEffect(
                    source=source.with_status(type(self)),
                    pid=source.pid,
                    element=this_char.ELEMENT,
                    num=1,
                ),
            ], replace(self, usages=-1, activated=False)
        elif signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


@dataclass(frozen=True, kw_only=True)
class LaurelCoronetStatus(_ElementalDiscountStatus):
    _ELEMENT: ClassVar[Element] = Element.DENDRO

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import LaurelCoronet
        return LaurelCoronet


@dataclass(frozen=True, kw_only=True)
class MaskOfSolitudeBasaltStatus(_ElementalDiscountStatus):
    _ELEMENT: ClassVar[Element] = Element.GEO

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import MaskOfSolitudeBasalt
        return MaskOfSolitudeBasalt


@dataclass(frozen=True, kw_only=True)
class OceanHuedClamStatus(_CrownOfWatatsumiStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.OceanHuedClam]:
        from ..card.card import OceanHuedClam
        return OceanHuedClam


@dataclass(frozen=True, kw_only=True)
class OrnateKabutoStatus(_OrnateKabutoStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.OrnateKabuto]:
        from ..card.card import OrnateKabuto
        return OrnateKabuto


@dataclass(frozen=True, kw_only=True)
class ShadowOfTheSandKingStatus(_ShadowOfTheSandKingLikeStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import ShadowOfTheSandKing
        return ShadowOfTheSandKing


@dataclass(frozen=True, kw_only=True)
class TenacityOfTheMillelithStatus(ArtifactEquipmentStatus, _UsageLivingStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_DMG,
        TriggeringSignal.ROUND_START,
        TriggeringSignal.ROUND_END,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import TenacityOfTheMillelith
        return TenacityOfTheMillelith

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_DMG:
            assert isinstance(detail, DmgIEvent)
            if not (
                    self._target_is_self_active(game_state, source)
                    and self.usages > 0
                    and detail.dmg.target == source
            ):
                return [], self
            this_char = game_state.get_character_target(source)
            assert this_char is not None
            return [
                eft.AddDiceEffect(
                    source=source.with_status(type(self)),
                    pid=source.pid,
                    element=this_char.ELEMENT,
                    num=1,
                ),
            ], replace(self, usages=-1)
        elif signal is TriggeringSignal.ROUND_START:
            return [
                eft.AddCharacterStatusEffect(
                    target=source,
                    status=UnmovableMountainStatus,
                ),
            ], self
        elif signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


@dataclass(frozen=True, kw_only=True)
class ThunderSummonersCrownStatus(_ElementalDiscountStatus):
    _ELEMENT: ClassVar[Element] = Element.ELECTRO

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import ThunderSummonersCrown
        return ThunderSummonersCrown


@dataclass(frozen=True, kw_only=True)
class ThunderingFuryStatus(_ElementalDiscountSupplyStatus):
    _ELEMENT: ClassVar[Element] = Element.ELECTRO

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import ThunderingFury
        return ThunderingFury


@dataclass(frozen=True, kw_only=True)
class ViridescentVenererStatus(_ElementalDiscountSupplyStatus):
    _ELEMENT: ClassVar[Element] = Element.ANEMO

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import ViridescentVenerer
        return ViridescentVenerer


@dataclass(frozen=True, kw_only=True)
class ViridescentVenerersDiademStatus(_ElementalDiscountStatus):
    _ELEMENT: ClassVar[Element] = Element.ANEMO

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import ViridescentVenerersDiadem
        return ViridescentVenerersDiadem


@dataclass(frozen=True, kw_only=True)
class VourukashasGlowStatus(_HeartOfKhvarenasBrillianceLikeStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        *_HeartOfKhvarenasBrillianceLikeStatus.REACTABLE_SIGNALS,
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import VourukashasGlow
        return VourukashasGlow

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT and self.usages < self.MAX_USAGES:
            return [
                eft.RecoverHPEffect(
                    source=source,
                    target=source,
                    recovery=1,
                ),
            ], self
        return super()._react_to_signal(game_state, source, signal, detail)


@dataclass(frozen=True, kw_only=True)
class WineStainedTricorneStatus(_ElementalDiscountStatus):
    _ELEMENT: ClassVar[Element] = Element.HYDRO

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import WineStainedTricorne
        return WineStainedTricorne


@dataclass(frozen=True, kw_only=True)
class WitchsScorchingHatStatus(_ElementalDiscountStatus):
    _ELEMENT: ClassVar[Element] = Element.PYRO

    @cached_classproperty
    def CARD(cls) -> type[crd.ArtifactEquipmentCard]:
        from ..card.card import WitchsScorchingHat
        return WitchsScorchingHat


############################## Combat Status ##############################


@dataclass(frozen=True, kw_only=True)
class AncientCourtyardStatus(CombatStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.CARD1_COST_OMNI:
            assert isinstance(item, CardPEvent)
            from ..card.card import WeaponEquipmentCard, ArtifactEquipmentCard
            if (
                    item.pid is status_source.pid
                    and issubclass(item.card_type, WeaponEquipmentCard | ArtifactEquipmentCard)
                    and item.dice_cost.can_cost_less_elem()
            ):
                new_cost = item.dice_cost.cost_less_elem(2)
                return item.with_new_cost(new_cost), None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True)
class CatalyzingFieldStatus(CombatStatus):
    damage_boost: ClassVar[int] = 1
    usages: int = 2

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, eft.DmgPEvent)
            dmg = item.dmg
            assert self.usages >= 1
            elem_can_boost = dmg.element is Element.ELECTRO or dmg.element is Element.DENDRO
            legal_to_boost = status_source.pid is dmg.source.pid and dmg.damage_type.can_boost()
            target_is_active = dmg.target.id == game_state.get_player(
                dmg.target.pid
            ).just_get_active_character().id
            if elem_can_boost and legal_to_boost and target_is_active:
                new_damage = replace(dmg, damage=dmg.damage + CatalyzingFieldStatus.damage_boost)
                new_item = DmgPEvent(dmg=new_damage)
                if self.usages == 1:
                    return new_item, None
                else:
                    return new_item, type(self)(self.usages - 1)
        return super()._preprocess(game_state, status_source, item, signal)

    def __str__(self) -> str:
        return super().__str__() + f"({self.usages})"  # pragma: no cover


@dataclass(frozen=True)
class ChangingShiftsStatus(CombatStatus):
    COST_DEDUCTION: ClassVar[int] = 1

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SWAP_COST_OMNI:
            assert isinstance(item, ActionPEvent) and item.event_type is EventType.SWAP
            if item.source.pid is status_source.pid \
                    and item.dice_cost.num_dice() >= self.COST_DEDUCTION:
                new_cost = item.dice_cost.cost_less_elem(self.COST_DEDUCTION)
                return item.with_new_cost(new_cost), None
        return super()._preprocess(game_state, status_source, item, signal)


@dataclass(frozen=True, kw_only=True)
class CrystallizeStatus(CombatStatus, StackedShieldStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 2


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
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | DendroCoreStatus]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            assert self.usages >= 1
            elem_can_boost = dmg.element is Element.ELECTRO or dmg.element is Element.PYRO
            legal_to_boost = status_source.pid is dmg.source.pid and dmg.damage_type.can_boost()
            target_is_active = dmg.target.id == game_state.get_player(
                dmg.target.pid
            ).just_get_active_character().id
            if elem_can_boost and legal_to_boost and target_is_active:
                new_damage = replace(dmg, damage=dmg.damage + DendroCoreStatus.damage_boost)
                new_item = DmgPEvent(dmg=new_damage)
                if self.usages == 1:
                    return new_item, None
                else:  # pragma: no cover
                    return new_item, DendroCoreStatus(self.usages - 1)
        return super()._preprocess(game_state, status_source, item, signal)

    # @override
    # def update(self, other: DendroCoreStatus) -> DendroCoreStatus:
    #     total_count = min(self.count + other.count, 2)
    #     return DendroCoreStatus(total_count)

    def __str__(self) -> str:
        return super().__str__() + f"({self.usages})"  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class ElementalResonanceEnduringRockStatus(CombatStatus):
    activated: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.ROUND_END,
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
                    not self.activated
                    and information.dmg.element is Element.GEO
                    and information.dmg.source.pid is status_source.pid
                    and information.dmg.damage_type.directly_from_character()
            ):
                return replace(self, activated=True)
                ...
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL:
            if not self.activated:
                return [], self
            combat_statuses = game_state.get_player(source.pid).combat_statuses
            stacked_shield_status = next((
                status
                for status in combat_statuses
                if isinstance(status, StackedShieldStatus)
            ), None)
            if stacked_shield_status is None:
                return [], replace(self, activated=False)
            assert isinstance(stacked_shield_status, CombatStatus)
            return [
                eft.OverrideCombatStatusEffect(
                    target_pid=source.pid,
                    status=replace(stacked_shield_status, usages=stacked_shield_status.usages + 3)
                )
            ], None
        elif signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class ElementalResonanceFerventFlamesStatus(CombatStatus):
    DMG_BOOST: ClassVar[int] = 3
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                    dmg.reaction is not None
                    and dmg.reaction.elem_reaction(Element.PYRO)
                    and dmg.damage_type.from_character()
                    and self._target_is_self_active(game_state, status_source, dmg.source)
            ):
                return replace(item, dmg=replace(dmg, damage=dmg.damage + self.DMG_BOOST)), None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class ElementalResonanceShatteringIceStatus(CombatStatus):
    DMG_BOOST: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                    dmg.damage_type.directly_from_character()
                    and self._target_is_self_active(game_state, status_source, dmg.source)
            ):
                return replace(item, dmg=replace(dmg, damage=dmg.damage + self.DMG_BOOST)), None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class ElementalResonanceSprawlingGreeneryStatus(CombatStatus):
    DMG_BOOST: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
        # TODO
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                    dmg.source.pid is status_source.pid
                    and dmg.reaction is not None
                    and dmg.damage_type.can_boost()
            ):
                return replace(item, dmg=replace(dmg, damage=dmg.damage + self.DMG_BOOST)), None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class IHaventLostYetOnCooldownStatus(CombatStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class LeaveItToMeStatus(CombatStatus):
    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SWAP:
            assert isinstance(item, ActionPEvent) and item.event_type is EventType.SWAP
            if item.source.pid is status_source.pid \
                    and item.event_speed is EventSpeed.COMBAT_ACTION:
                return replace(item, event_speed=EventSpeed.FAST_ACTION), None
        return super()._preprocess(game_state, status_source, item, signal)


@dataclass(frozen=True, kw_only=True)
class LyresongStatus(CombatStatus):
    COST_DEDUCTION: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
        if signal is Preprocessables.CARD1_COST_OMNI:
            assert isinstance(item, CardPEvent)
            from ..card.card import ArtifactEquipmentCard
            if (
                    item.pid is status_source.pid
                    and issubclass(item.card_type, ArtifactEquipmentCard)
                    and item.dice_cost.can_cost_less_elem()
            ):
                return item.with_new_cost(item.dice_cost.cost_less_elem(self.COST_DEDUCTION)), None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class MillennialMovementFarewellSongStatus(CombatStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            if (
                    item.dmg.source.pid is status_source.pid
                    and item.dmg.damage_type.directly_from_character()
            ):
                return item.delta_damage(1), self
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class PassingOfJudgmentStatus(CombatStatus, _UsageStatus):
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 3
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.CARD1:
            assert isinstance(item, CardPEvent)
            from ..card.card import EventCard
            if (
                    item.pid is status_source.pid
                    and not item.invalidated
                    and issubclass(item.card_type, EventCard)
            ):
                return item.invalidate(), replace(self, usages=self.usages - 1)
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class RebelliousShieldStatus(CombatStatus, StackedShieldStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 2


@dataclass(frozen=True, kw_only=True)
class RedFeatherFanStatus(CombatStatus):
    used: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SWAP_COST_OMNI:
            assert isinstance(item, ActionPEvent)
            if (
                    item.source.pid is status_source.pid
                    and item.dice_cost.can_cost_less_elem()
            ):
                return item.with_new_cost(item.dice_cost.cost_less_elem(1)), replace(self, used=True)
        elif signal is Preprocessables.SWAP:
            assert isinstance(item, ActionPEvent)
            if (
                    item.source.pid is status_source.pid
                    and (
                        item.is_combat_action()
                        or self.used
                    )
            ):
                return item.make_fast_action(), None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class ReviveOnCooldownStatus(CombatStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class FreshWindOfFreedomStatus(CombatStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_DMG,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_DMG:
            assert isinstance(detail, DmgIEvent)
            if (
                    detail.lethal
                    and detail.dmg.target.pid is source.pid.other
                    and game_state.get_player(source.pid).in_action_phase()
            ):
                return [eft.ConsecutiveActionEffect(target_pid=source.pid)], None
        elif signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class SandAndDreamsStatus(CombatStatus):
    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SKILL_COST_OMNI:
            assert isinstance(item, ActionPEvent)
            if (
                    status_source.pid is item.source.pid
                    and item.event_type.is_skill()
                    and item.dice_cost.can_cost_less_elem()
            ):
                return item.with_new_cost(item.dice_cost.cost_less_elem(3)), None
        return item, self


@dataclass(frozen=True, kw_only=True)
class StoneAndContractsStatus(CombatStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_START,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_START:
            return [
                eft.AddDiceEffect(
                    source=source.with_status(type(self)),
                    pid=source.pid,
                    element=Element.OMNI,
                    num=3,
                ),
                eft.DrawTopCardEffect(
                    pid=source.pid,
                    num=1,
                ),
            ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class SunyataFlowerStatus(CombatStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
        if signal is Preprocessables.CARD1_COST_OMNI:
            assert isinstance(item, CardPEvent)
            from ..card.card import SupportCard
            if (
                    item.pid is status_source.pid
                    and issubclass(item.card_type, SupportCard)
                    and item.dice_cost.can_cost_less_elem()
            ):
                return item.with_new_cost(item.dice_cost.cost_less_elem(1)), None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class TheBoarPrincessStatus(CombatStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    triggered_num: int = 0
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.DEATH_EVENT,
        TriggeringSignal.POST_CARD,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _inform(
            self, game_state: GameState, status_source: StaticTarget, info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.EQUIPMENT_DISCARDING:
            assert isinstance(information, EquipmentDiscardIEvent)
            if (
                    information.target.pid is status_source.pid
                    and issubclass(
                        information.status,
                        WeaponEquipmentStatus | ArtifactEquipmentStatus,
                    )
            ):
                return replace(self, triggered_num=self.triggered_num + 1)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if (
                (
                    signal is TriggeringSignal.DEATH_EVENT
                    or signal is TriggeringSignal.POST_CARD
                )
                and self.triggered_num > 0
        ):
            assert self.usages > 0
            usable_usages = min(self.usages, self.triggered_num)
            return [
                eft.AddDiceEffect(
                    source=source.with_status(type(self)),
                    pid=source.pid,
                    element=Element.OMNI,
                    num=usable_usages,
                ),
            ], replace(self, usages=-usable_usages, triggered_num=0)
        elif signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self

    def __str__(self) -> str:
        return super().__str__() + f"({self.triggered_num})"  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class WhenTheCraneReturnedStatus(CombatStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
    ))
    triggered: bool = False

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
            if information.source.pid is status_source.pid and not self.triggered:
                return replace(self, triggered=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.triggered:
            return [
                eft.ForwardSwapCharacterEffect(source.pid),
            ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class WhereIsTheUnseenRazorStatus(CombatStatus):
    COST_DEDUCTION: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.CARD1_COST_OMNI:
            assert isinstance(item, CardPEvent)
            from ..card.card import WeaponEquipmentCard
            if (
                    item.pid is status_source.pid
                    and issubclass(item.card_type, WeaponEquipmentCard)
                    and item.dice_cost.can_cost_less_elem()
            ):
                return item.with_new_cost(item.dice_cost.cost_less_elem(self.COST_DEDUCTION)), None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class WindAndFreedomStatus(CombatStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.ROUND_END,
    ))
    triggered: bool = False

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
            if information.source.pid is status_source.pid and not self.triggered:
                return replace(self, triggered=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.triggered:
            return [
                eft.ForwardSwapCharacterEffect(source.pid),
            ], replace(self, triggered=False)
        elif signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


############################## Character Status ##############################

@dataclass(frozen=True, kw_only=True)
class AdeptusTemptationStatus(CharacterStatus):
    DMG_BOOST: ClassVar[int] = 3
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                    dmg.source == status_source
                    and dmg.damage_type.direct_elemental_burst()
                    and dmg.damage_type.can_boost()
            ):
                return item.delta_damage(self.DMG_BOOST), None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class ButterCrabStatus(CharacterStatus, StackedShieldStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    SHIELD_AMOUNT: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class FishAndChipsStatus(CharacterStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SKILL_COST_OMNI:
            assert isinstance(item, ActionPEvent)
            if (
                    item.source == status_source
                    and item.event_type.is_skill()
                    and item.dice_cost.can_cost_less_elem()
            ):
                return item.with_new_cost(item.dice_cost.cost_less_elem(1)), None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True)
class FrozenStatus(CharacterStatus):
    damage_boost: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            can_reaction = dmg.element is Element.PYRO or dmg.element is Element.PHYSICAL
            is_damage_target = dmg.target == status_source
            if is_damage_target and can_reaction:
                return (
                    DmgPEvent(dmg=replace(dmg, damage=dmg.damage + FrozenStatus.damage_boost)),
                    None
                )
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class HeavyStrikeStatus(CharacterStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            if (
                    item.dmg.source == status_source
                    and item.dmg.damage_type.direct_normal_attack()
            ):
                if item.dmg.damage_type.charged_attack:
                    return item.delta_damage(2), None
                else:
                    return item.delta_damage(1), None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover

@dataclass(frozen=True)
class JueyunGuobaStatus(CharacterStatus, _UsageStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    DAMAGE_BOOST: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if dmg.source == status_source and dmg.damage_type.direct_normal_attack():
                dmg = replace(dmg, damage=dmg.damage + JueyunGuobaStatus.DAMAGE_BOOST)
                return DmgPEvent(dmg=dmg), replace(self, usages=self.usages - 1)
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class KingsSquireEffectStatus(CharacterStatus, _SkillCostReductionStatus):
    COST_DEDUCTION: ClassVar[int] = 2
    DISCOUNTED_SKILL_TYPES: ClassVar[frozenset[CharacterSkillType]] = frozenset((
        CharacterSkillType.ELEMENTAL_SKILL,
    ))


@dataclass(frozen=True, kw_only=True)
class LithicGuardStatus(CharacterStatus, StackedShieldStatus):
    MAX_USAGES: ClassVar[int] = 3


@dataclass(frozen=True)
class LotusFlowerCrispStatus(CharacterStatus, FixedShieldStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    SHIELD_AMOUNT: ClassVar[int] = 3
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        d_usages = 0
        if signal is TriggeringSignal.ROUND_END:
            d_usages = -BIG_INT
        return [], replace(self, usages=d_usages)


@dataclass(frozen=True)
class MintyMeatRollsStatus(CharacterStatus, _UsageStatus):
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 3
    COST_DEDUCTION: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
        if signal is Preprocessables.SKILL_COST_ANY:
            assert isinstance(item, ActionPEvent)
            if (
                    status_source == item.source
                    and item.event_sub_type is CharacterSkillType.NORMAL_ATTACK
                    and item.dice_cost.can_cost_less_any()
            ):
                return (
                    item.with_new_cost(item.dice_cost.cost_less_any(self.COST_DEDUCTION)),
                    replace(self, usages=self.usages - 1),
                )
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        d_usages = 0
        if signal is TriggeringSignal.ROUND_END:
            d_usages = -BIG_INT
        return [], replace(self, usages=d_usages)


@dataclass(frozen=True, kw_only=True)
class MoonpiercerEffectStatus(CharacterStatus, _SkillCostReductionStatus):
    COST_DEDUCTION: ClassVar[int] = 2
    DISCOUNTED_SKILL_TYPES: ClassVar[frozenset[CharacterSkillType]] = frozenset((
        CharacterSkillType.ELEMENTAL_SKILL,
    ))


@dataclass(frozen=True)
class MushroomPizzaStatus(CharacterStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.END_ROUND_CHECK_OUT,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        es: list[eft.Effect] = []
        d_usages = 0
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            es.append(
                eft.RecoverHPEffect(
                    source=source,
                    target=source,
                    recovery=1,
                )
            )
        if signal is TriggeringSignal.ROUND_END:
            d_usages = -1

        return es, replace(self, usages=d_usages)


@dataclass(frozen=True)
class NorthernSmokedChickenStatus(CharacterStatus):
    COST_DEDUCTION: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SKILL_COST_ANY:
            assert isinstance(item, ActionPEvent)
            if (
                    status_source == item.source
                    and item.event_sub_type is CharacterSkillType.NORMAL_ATTACK
                    and item.dice_cost.can_cost_less_any()
            ):
                return item.with_new_cost(item.dice_cost.cost_less_any(self.COST_DEDUCTION)), None
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class SashimiPlatterStatus(CharacterStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            if (
                    item.dmg.source == status_source
                    and item.dmg.damage_type.direct_normal_attack()
            ):
                return item.delta_damage(1), self
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover


@dataclass(frozen=True)
class SatiatedStatus(CharacterStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class TandooriRoastChickenStatus(CharacterStatus):
    DMG_BOOST: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                dmg.source == status_source
                and dmg.damage_type.direct_elemental_skill()
                and dmg.element is not Element.PIERCING
            ):
                return item.delta_damage(self.DMG_BOOST), None
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class UnmovableMountainStatus(CharacterStatus, StackedShieldStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self  # pragma: no cover


############################## Character Specific Status ##############################
"""
Group statues by characters, characters ordered alphabetically
"""

#### Albedo ####


@dataclass(frozen=True, kw_only=True)
class DescentOfDivinityStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import DescentOfDivinity
        return DescentOfDivinity


#### Arataki Itto ####


@dataclass(frozen=True, kw_only=True)
class AratakiIchibanStatus(TalentEquipmentStatus, _UsageLivingStatus):
    usages: int = 0  # here means num of normal attacks in the past
    ACTIVATION_THRESHOLD: ClassVar[int] = 2
    DAMAGE_BOOST: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import AratakiIchiban
        return AratakiIchiban

    def activated(self) -> bool:
        return self.usages + 1 >= self.ACTIVATION_THRESHOLD

    @property
    def dmg_boost(self) -> int:
        return self.DAMAGE_BOOST

    @override
    def _inform(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if self.activated() \
                or info_type is not Informables.POST_SKILL_USAGE:
            return self

        assert isinstance(information, SkillIEvent)
        if status_source != information.source \
                or information.skill_type != CharacterSkill.SKILL1:
            return self

        return replace(self, usages=self.usages + 1)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-self.usages)
        return [], self  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class RagingOniKingStatus(CharacterStatus, _InfusionStatus):
    usages: int = 2  # duration
    ELEMENT: ClassVar[Element] = Element.GEO
    DAMAGE_BOOST: ClassVar[int] = 1
    status_gaining_usages: int = 1
    status_gaining_available: bool = False

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _dmg_boost_condition(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: eft.SpecificDamageEffect,
    ) -> bool:
        return (
            super()._dmg_boost_condition(game_state, status_source, item)
            and item.damage_type.direct_normal_attack()
        )

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
            if information.source == status_source \
                    and information.skill_type is CharacterSkill.SKILL1 \
                    and not self.status_gaining_available:
                return replace(self, status_gaining_available=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-1)
        elif signal is TriggeringSignal.POST_SKILL:
            if self.status_gaining_available:
                return [
                    eft.AddCharacterStatusEffect(
                        target=source,
                        status=SuperlativeSuperstrengthStatus,
                    ),
                ], replace(self, usages=0, status_gaining_usages=0, status_gaining_available=False)
        return [], self


@dataclass(frozen=True, kw_only=True)
class SuperlativeSuperstrengthStatus(CharacterStatus, _UsageStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 3
    DAMAGE_BOOST: ClassVar[int] = 1
    TALENT_DAMAGE_BOOST: ClassVar[int] = 1
    COST_DEDUCTION: ClassVar[int] = 1

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if status_source != dmg.source:
                return item, self
            if dmg.damage_type.direct_charged_attack():
                character = game_state.get_character_target(status_source)
                assert character is not None, f"source {status_source} in {game_state}"
                dmg_boost = self.DAMAGE_BOOST
                if character.talent_equipped():
                    talent = character.character_statuses.just_find(AratakiIchibanStatus)
                    if talent.activated():
                        dmg_boost += talent.dmg_boost
                new_item = DmgPEvent(dmg=replace(dmg, damage=dmg.damage + dmg_boost))
                new_self = replace(self, usages=self.usages - 1)
                return new_item, new_self
        elif signal is Preprocessables.SKILL_COST_ANY:
            assert isinstance(item, ActionPEvent)
            player = game_state.get_player(status_source.pid)
            if (
                    self.usages >= 2
                    and status_source == item.source
                    and item.event_type is EventType.SKILL1
                    and player.dice.is_even()
                    and item.dice_cost.can_cost_less_any()
            ):
                return item.with_new_cost(item.dice_cost.cost_less_any(self.COST_DEDUCTION)), self
        return item, self


#### Bennett ####


@dataclass(frozen=True, kw_only=True)
class GrandExpectationStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import GrandExpectation
        return GrandExpectation


@dataclass(frozen=True, kw_only=True)
class _InspirationFieldStatus(CombatStatus, _UsageStatus):
    usages: int = 2  # duration
    activated: bool = False
    target_char_id: None | int = None
    MAX_USAGES: ClassVar[int] = 2
    DMG_BOOST: ClassVar[int] = 2
    BOOST_LOCK: ClassVar[bool]
    HP_CAP: ClassVar[int] = 7
    RECOVERY: ClassVar[int] = 2

    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.ROUND_END,
    })

    def _boostable(self, char: Character) -> bool:
        return not self.BOOST_LOCK or char.hp >= self.HP_CAP

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
            if (
                    not self.activated
                    and information.source.pid is status_source.pid
            ):
                assert self.target_char_id is None
                assert isinstance(information.source.id, int)
                return replace(self, activated=True, target_char_id=information.source.id)
        return self

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
            active_char = game_state.get_player(status_source.pid).just_get_active_character()
            active_char_source = StaticTarget(
                status_source.pid,
                Zone.CHARACTERS,
                active_char.id,
            )
            if not (
                    item.dmg.source == active_char_source
                    and item.dmg.damage_type.directly_from_character()
                    and self._boostable(active_char)
            ):
                return item, self
            return replace(item, dmg=replace(
                item.dmg, damage=item.dmg.damage + self.DMG_BOOST
            )), self
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.activated:
            assert self.target_char_id is not None
            target = StaticTarget.from_char_id(source.pid, self.target_char_id)
            char = game_state.get_character_target(target)
            assert char is not None
            if char.hp >= self.HP_CAP:
                return [], replace(self, usages=0, activated=False, target_char_id=None)
            return [
                eft.RecoverHPEffect(
                    source=source,
                    target=target,
                    recovery=self.RECOVERY,
                )
            ], replace(self, usages=0, activated=False, target_char_id=None)
        if signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class InspirationFieldStatus(_InspirationFieldStatus):
    BOOST_LOCK: ClassVar[bool] = True


@dataclass(frozen=True, kw_only=True)
class InspirationFieldEnhancedStatus(_InspirationFieldStatus):
    BOOST_LOCK: ClassVar[bool] = False

#### Chongyun ####


def _chongyun_infusion_condition(game_state: GameState, dmg: eft.SpecificDamageEffect) -> bool:
    """ Chongyun's infusion condition: normal attack of claymore, polearm, or sword. """
    return (
        dmg.damage_type.direct_normal_attack()
        and (char := game_state.get_character_target(dmg.source)) is not None
        and char.WEAPON_TYPE in {WeaponType.CLAYMORE, WeaponType.POLEARM, WeaponType.SWORD}
    )


@dataclass(frozen=True, kw_only=True)
class ChonghuasFrostFieldEnhancedStatus(CombatStatus, _InfusionStatus):
    usages: int = 2
    ELEMENT: ClassVar[Element] = Element.CRYO
    DAMAGE_BOOST: ClassVar[int] = 1

    @override
    def _dmg_element_condition(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: eft.SpecificDamageEffect,
    ) -> bool:
        return _chongyun_infusion_condition(game_state, item) and item.element is Element.PHYSICAL

    @override
    def _dmg_boost_condition(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: eft.SpecificDamageEffect,
    ) -> bool:
        return _chongyun_infusion_condition(game_state, item)


@dataclass(frozen=True, kw_only=True)
class ChonghuasFrostFieldStatus(CombatStatus, _InfusionStatus):
    usages: int = 2
    ELEMENT: ClassVar[Element] = Element.CRYO

    @override
    def _dmg_element_condition(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: eft.SpecificDamageEffect,
    ) -> bool:
        return _chongyun_infusion_condition(game_state, item) and item.element is Element.PHYSICAL


@dataclass(frozen=True, kw_only=True)
class SteadyBreathingStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import SteadyBreathing
        return SteadyBreathing


#### Collei ####

@dataclass(frozen=True, kw_only=True)
class ColleiTalentStatus(CharacterHiddenStatus):
    """ Saves the elemental skill usages of Collei per round """
    elemental_skill_used: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
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
            if (
                    not self.elemental_skill_used
                    and information.source == status_source
                    and information.skill_type is CharacterSkill.SKILL2
            ):
                return replace(self, elemental_skill_used=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END and self.elemental_skill_used:
            return [], replace(self, elemental_skill_used=False)
        return [], self


@dataclass(frozen=True, kw_only=True)
class FloralSidewinderStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import FloralSidewinder
        return FloralSidewinder


@dataclass(frozen=True, kw_only=True)
class SproutStatus(CombatStatus, _UsageStatus):
    activated: bool = False
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.ROUND_END,
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
            dmg = information.dmg
            if (
                    not self.activated
                    and dmg.source.pid is status_source.pid
                    and dmg.reaction is not None
                    and dmg.reaction.elem_reaction(Element.DENDRO)
                    and dmg.damage_type.directly_from_character()
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
                    element=Element.DENDRO,
                    damage=1,
                    damage_type=DamageType(status=True),
                )
            ], replace(self, usages=-1, activated=False)
        elif signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-1)
        return [], self


#### Dehya ####


@dataclass(frozen=True, kw_only=True)
class IncinerationDriveStatus(CharacterStatus, PrepareSkillStatus):
    DAMAGE: ClassVar[int] = 3
    DMG_ELEM: ClassVar[Element] = Element.PYRO

    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.ACT_PRE_SKILL,
        TriggeringSignal.SELF_SWAP,
    })

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ACT_PRE_SKILL:
            return [
                eft.RemoveCharacterStatusEffect(
                    target=source,
                    status=type(self),
                ),
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=self.DMG_ELEM,
                    damage=self.DAMAGE,
                    damage_type=DamageType(elemental_burst=True, status=True),
                ),
            ], self
        elif signal is TriggeringSignal.SELF_SWAP:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class StalwartAndTrueStatus(TalentEquipmentStatus):
    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.END_ROUND_CHECK_OUT,
    })

    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import StalwartAndTrue
        return StalwartAndTrue

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            this_char = game_state.get_character_target(source)
            assert this_char is not None
            if (
                    this_char.is_alive()
                    and this_char.hp <= 6
            ):
                return [eft.RecoverHPEffect(
                    source=source,
                    target=source,
                    recovery=2,
                )], self
        return [], self


#### Diona ####


@dataclass(frozen=True, kw_only=True)
class CatClawShieldEnhancedStatus(StackedShieldStatus, CombatStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2


@dataclass(frozen=True, kw_only=True)
class CatClawShieldStatus(StackedShieldStatus, CombatStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1


@dataclass(frozen=True, kw_only=True)
class ShakenNotPurredStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import ShakenNotPurred
        return ShakenNotPurred


#### Electro Hypostasis ####


@dataclass(frozen=True, kw_only=True)
class ElectroHypostasisPassiveStatus(CharacterHiddenStatus):
    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.INIT_GAME_START,
    })

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.INIT_GAME_START:
            return [
                eft.AddCharacterStatusEffect(
                    target=source,
                    status=ElectroCrystalCoreStatus,
                )
            ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class ElectroCrystalCoreStatus(CharacterStatus, RevivalStatus):
    _HEAL_AMOUNT: ClassVar[int] = 3
    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.TRIGGER_REVIVAL,
    })

    @override
    def revivable(
            self, game_state: GameState, status_source: StaticTarget, char_source: StaticTarget,
    ) -> bool:
        return status_source == char_source

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.TRIGGER_REVIVAL:
            character = game_state.get_character_target(source)
            assert character is not None
            assert character.hp == 0
            return [], None
        return [], self

    @override
    def _post_update_react_to_signal(
            self,
            game_state: GameState,
            effects: list[eft.Effect],
            source: StaticTarget,
            signal: TriggeringSignal,
            detail: None | InformableEvent,
    ) -> list[eft.Effect]:
        if signal is TriggeringSignal.TRIGGER_REVIVAL:
            effects.append(
                eft.ReviveRecoverHPEffect(
                    source=source,
                    target=source,
                    recovery=self._HEAL_AMOUNT,
                )
            )
        return effects


@dataclass(frozen=True, kw_only=True)
class RockPaperScissorsComboPaperStatus(CharacterStatus, PrepareSkillStatus):
    DAMAGE: ClassVar[int] = 3

    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.ACT_PRE_SKILL,
        TriggeringSignal.SELF_SWAP,
    })

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ACT_PRE_SKILL:
            return [
                eft.RemoveCharacterStatusEffect(
                    target=source,
                    status=type(self),
                ),
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.ELECTRO,
                    damage=self.DAMAGE,
                    damage_type=DamageType(elemental_skill=True, status=True),
                ),
            ], self
        elif signal is TriggeringSignal.SELF_SWAP:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class RockPaperScissorsComboScissorsStatus(CharacterStatus, PrepareSkillStatus):
    DAMAGE: ClassVar[int] = 2

    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.ACT_PRE_SKILL,
        TriggeringSignal.SELF_SWAP,
    })

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ACT_PRE_SKILL:
            return [
                eft.RemoveCharacterStatusEffect(
                    target=source,
                    status=type(self),
                ),
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.ELECTRO,
                    damage=self.DAMAGE,
                    damage_type=DamageType(elemental_skill=True, status=True),
                ),
                eft.AddCharacterStatusEffect(
                    target=source,
                    status=RockPaperScissorsComboPaperStatus,
                ),
            ], self
        elif signal is TriggeringSignal.SELF_SWAP:
            return [], None
        return [], self



#### Eula ####

@dataclass(frozen=True, kw_only=True)
class GrimheartStatus(CharacterStatus):
    activated: bool = False
    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.POST_SKILL,
    })

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
                    item.dmg.source == status_source
                    and item.dmg.damage_type.direct_elemental_skill()
                    and not self.activated
            ):
                return item.delta_damage(3), replace(self, activated=True)
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.activated:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class WellspingOfWarLustStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import WellspingOfWarLust
        return WellspingOfWarLust


#### Fatui Cryo Cicin Mage ####

@dataclass(frozen=True, kw_only=True)
class CicinsColdGlareStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import CicinsColdGlare
        return CicinsColdGlare


@dataclass(frozen=True, kw_only=True)
class FlowingCicinShieldStatus(CharacterStatus, StackedShieldStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 4


#### Fatui Pyro Agent ####

@dataclass(frozen=True, kw_only=True)
class PaidInFullStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import PaidInFull
        return PaidInFull


@dataclass(frozen=True, kw_only=True)
class StealthMasterStatus(CharacterHiddenStatus):
    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.INIT_GAME_START,
    })

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.INIT_GAME_START:
            return [
                eft.AddCharacterStatusEffect(
                    target=source,
                    status=StealthStatus,
                )
            ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class StealthStatus(CharacterStatus, FixedShieldStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    SHIELD_AMOUNT: ClassVar[int] = 1
    DAMAGE_BOOST: ClassVar[int] = 1
    INFUSION_ELEMENT: ClassVar[Element] = Element.PYRO

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
            if dmg.source == status_source and dmg.damage_type.directly_from_character():
                return item.delta_damage(self.DAMAGE_BOOST), replace(self, usages=self.usages - 1)
        elif signal is Preprocessables.DMG_ELEMENT:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if not (
                    dmg.source == status_source
                    and dmg.element is Element.PHYSICAL
                    and dmg.damage_type.directly_from_character()
            ):
                return item, self
            char = game_state.get_character_target(status_source)
            assert char is not None
            if not char.talent_equipped():
                return item, self
            return item.convert_element(self.INFUSION_ELEMENT), self

        return super()._preprocess(game_state, status_source, item, signal)


#### Fischl ####

@dataclass(frozen=True, kw_only=True)
class StellarPredatorStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import StellarPredator
        return StellarPredator


#### Ganyu ####

@dataclass(frozen=True, kw_only=True)
class GanyuTalentStatus(CharacterHiddenStatus):
    elemental_skill2ed: bool = False

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
            if information.is_skill_from_character(
                    game_state,
                    status_source.pid,
                    CharacterSkill.SKILL3,
            ):
                return replace(self, elemental_skill2ed=True)
        return self


@dataclass(frozen=True, kw_only=True)
class IceLotusStatus(CombatStatus, FixedShieldStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    SHIELD_AMOUNT: ClassVar[int] = 1


@dataclass(frozen=True, kw_only=True)
class UndividedHeartStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import UndividedHeart
        return UndividedHeart


#### Hu Tao ####


@dataclass(frozen=True, kw_only=True)
class BloodBlossomStatus(CharacterStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            return [
                eft.SpecificDamageEffect(
                    source=source,
                    target=source,
                    element=Element.PYRO,
                    damage=1,
                    damage_type=DamageType(no_boost=True, status=True),
                )
            ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class ParamitaPapilioStatus(CharacterStatus, _InfusionStatus):
    usages: int = 2
    ELEMENT: ClassVar[Element] = Element.PYRO
    DAMAGE_BOOST: ClassVar[int] = 1


@dataclass(frozen=True, kw_only=True)
class SanguineRougeStatus(TalentEquipmentStatus):

    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import SanguineRouge
        return SanguineRouge

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
            this_char = game_state.get_character_target(status_source)
            assert this_char is not None
            if (
                    item.dmg.source == status_source
                    and item.dmg.element is Element.PYRO
                    and item.dmg.damage_type.directly_from_character()
                    and this_char.hp <= 6
            ):
                return item.delta_damage(1), self
        return item, self


#### Jadeplume Terrorshroom ##

@dataclass(frozen=True, kw_only=True)
class ProliferatingSporesStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import ProliferatingSpores
        return ProliferatingSpores


@dataclass(frozen=True, kw_only=True)
class RadicalVitalityHiddenStatus(CharacterHiddenStatus):
    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.INIT_GAME_START,
        TriggeringSignal.REVIVAL_GAME_START,
    })

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if (
                signal is TriggeringSignal.INIT_GAME_START
                or signal is TriggeringSignal.REVIVAL_GAME_START
        ):
            return [
                eft.AddCharacterStatusEffect(
                    target=source,
                    status=RadicalVitalityStatus,
                )
            ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class RadicalVitalityStatus(CharacterStatus, _UsageLivingStatus):
    activated: bool = False
    to_clear: bool = False
    usages: int = 0
    NOMINAL_MAX_USAGES: ClassVar[int] = 3
    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.POST_DMG,
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.END_ROUND_CHECK_OUT,
    })

    def max_usages(self, game_state: GameState, source: StaticTarget) -> int:
        return self.NOMINAL_MAX_USAGES + self.talent_equiped(game_state, source)

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
            dmg = information.dmg
            if (
                    not self.activated
                    and dmg.source == status_source
                    and dmg.element.is_pure()
                    and dmg.damage_type.directly_from_character()
                    and self.usages < self.max_usages(game_state, status_source)
            ):
                return replace(self, activated=True)
        return self

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
            if (
                    dmg.source == status_source
                    and dmg.damage_type.direct_elemental_burst()
            ):
                return item.delta_damage(self.usages), replace(self, to_clear=True)
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_DMG:
            assert isinstance(detail, DmgIEvent)
            if (
                    detail.dmg.target == source
                    and detail.dmg.element.is_pure()
                    and self.usages < self.max_usages(game_state, source)
            ):
                return [], replace(self, usages=1)
        elif signal is TriggeringSignal.POST_SKILL:
            d_usages = 0
            if self.activated:
                d_usages = 1
            if self.to_clear:
                d_usages = -self.usages
            d_usages = min(d_usages, self.max_usages(game_state, source) - self.usages)
            if d_usages == 0:
                return [], self
            return [], replace(self, usages=d_usages, activated=False, to_clear=False)
        elif signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            if self.usages >= self.max_usages(game_state, source):
                char = game_state.get_character_target(source)
                assert char is not None
                return [
                    eft.EnergyDrainEffect(
                        target=source,
                        drain=char.max_energy,
                    ),
                ], replace(self, usages=-self.usages)
        return [], self

    def __str__(self) -> str:
        return super().__str__() + \
            f"({'*' if self.activated else '' }|{'*' if self.to_clear else ''})"


#### Jean ####

@dataclass(frozen=True, kw_only=True)
class LandsOfDandelionStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import LandsOfDandelion
        return LandsOfDandelion


#### Kaedehara Kazuha ####


@dataclass(frozen=True, kw_only=True)
class ChihayaburuStatus(CharacterHiddenStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL:
            return [
                eft.ForwardSwapCharacterEffect(
                    target_player=source.pid,
                ),
            ], None
        return [], self

@dataclass(frozen=True, kw_only=True)
class MidareRanzanStatus(CharacterStatus, PrepareSkillStatus):
    MAX_USAGES: ClassVar[int] = 1
    fast_swap_available: bool = True
    _ELEMENT: ClassVar[Element] = Element.ANEMO
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ACT_PRE_SKILL,
        TriggeringSignal.POST_SKILL,
    ))

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_ELEMENT:
            assert isinstance(item, DmgPEvent)
            if (
                    item.dmg.source == status_source
                    and item.dmg.damage_type.direct_normal_attack()
                    and item.dmg.element is Element.PHYSICAL
            ):
                return item.convert_element(self._ELEMENT), self
        elif signal is Preprocessables.SWAP and self.fast_swap_available:
            assert isinstance(item, ActionPEvent) and item.event_type is EventType.SWAP
            if (
                    item.target == status_source
                    and item.is_combat_action()
            ):
                return item.make_fast_action(), replace(self, fast_swap_available=False)
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL:
            assert isinstance(detail, SkillIEvent)
            if detail.source == source and detail.skill_type.is_skill1():
                return [], None
        elif signal is TriggeringSignal.ACT_PRE_SKILL:
            return [eft.CastSkillEffect(
                target=source,
                skill=CharacterSkill.SKILL1,
            )], self
        return [], self


@dataclass(frozen=True, kw_only=True)
class MidareRanzanCryoStatus(MidareRanzanStatus):
    _ELEMENT: ClassVar[Element] = Element.CRYO


@dataclass(frozen=True, kw_only=True)
class MidareRanzanElectroStatus(MidareRanzanStatus):
    _ELEMENT: ClassVar[Element] = Element.ELECTRO


@dataclass(frozen=True, kw_only=True)
class MidareRanzanHydroStatus(MidareRanzanStatus):
    _ELEMENT: ClassVar[Element] = Element.HYDRO


@dataclass(frozen=True, kw_only=True)
class MidareRanzanPyroStatus(MidareRanzanStatus):
    _ELEMENT: ClassVar[Element] = Element.PYRO


_MIDARE_RANZAN_MAP: dict[Element, type[MidareRanzanStatus]] = HashableDict({
    Element.ANEMO: MidareRanzanStatus,
    Element.CRYO: MidareRanzanCryoStatus,
    Element.ELECTRO: MidareRanzanElectroStatus,
    Element.HYDRO: MidareRanzanHydroStatus,
    Element.PYRO: MidareRanzanPyroStatus,
})


@dataclass(frozen=True, kw_only=True)
class PoeticsOfFuubutsuStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import PoeticsOfFuubutsu
        return PoeticsOfFuubutsu


@dataclass(frozen=True, kw_only=True)
class _PoeticsOfFuubutsuElementStatus(CombatStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    _ELEM: Element
    _DMG_BOOST: ClassVar[int] = 1
    _BOOSTABLE_ELEMS: ClassVar[frozenset[Element]] = Reaction.SWIRL.value.reaction_elems[0]

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
            if (
                    status_source.pid != dmg.source.pid
                    or not (
                        dmg.damage_type.directly_from_character()
                        or dmg.damage_type.directly_from_summon()
                    )
                    or dmg.element is not self._ELEM
            ):
                return item, self

            assert self.usages > 0
            new_item = DmgPEvent(dmg=replace(dmg, damage=dmg.damage + self._DMG_BOOST))
            return new_item, replace(self, usages=self.usages - 1)
        return item, self


@dataclass(frozen=True, kw_only=True)
class PoeticsOfFuubutsuCryoStatus(_PoeticsOfFuubutsuElementStatus):
    _ELEM: Element = Element.CRYO


@dataclass(frozen=True, kw_only=True)
class PoeticsOfFuubutsuElectroStatus(_PoeticsOfFuubutsuElementStatus):
    _ELEM: Element = Element.ELECTRO


@dataclass(frozen=True, kw_only=True)
class PoeticsOfFuubutsuHydroStatus(_PoeticsOfFuubutsuElementStatus):
    _ELEM: Element = Element.HYDRO


@dataclass(frozen=True, kw_only=True)
class PoeticsOfFuubutsuPyroStatus(_PoeticsOfFuubutsuElementStatus):
    _ELEM: Element = Element.PYRO


_POETICS_OF_FUUBUTSU_MAP: dict[Element, type[_PoeticsOfFuubutsuElementStatus]] = HashableDict({
    Element.CRYO: PoeticsOfFuubutsuCryoStatus,
    Element.ELECTRO: PoeticsOfFuubutsuElectroStatus,
    Element.HYDRO: PoeticsOfFuubutsuHydroStatus,
    Element.PYRO: PoeticsOfFuubutsuPyroStatus,
})

#### Kaeya ####


@dataclass(frozen=True, kw_only=True)
class IcicleStatus(CombatStatus, _UsageStatus):
    usages: int = 3
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.SELF_SWAP,
    ))

    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | IcicleStatus]:
        if signal is TriggeringSignal.SELF_SWAP:
            effects: list[eft.Effect] = [
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.CRYO,
                    damage=2,
                    damage_type=DamageType(status=True),
                ),
            ]
            return effects, replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class ColdBloodedStrikeStatus(TalentEquipmentStatus):
    """
    Equipping this status implies the equipped character is Kaeya
    """
    usages: int = 1
    activated: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.ROUND_END,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import ColdBloodedStrike
        return ColdBloodedStrike

    @override
    def _inform(
            self, game_state: GameState, status_source: StaticTarget, info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if self.activated or self.usages == 0:
            return self

        if info_type is not Informables.POST_SKILL_USAGE:
            return self

        assert isinstance(information, SkillIEvent)
        if status_source != information.source \
                or information.skill_type != CharacterSkill.SKILL2:
            return self

        return replace(self, activated=True)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        es: list[eft.Effect] = []
        new_self = self

        if signal is TriggeringSignal.POST_SKILL and self.activated:
            assert self.usages >= 1
            es.append(
                eft.RecoverHPEffect(
                    source=source,
                    target=source,
                    recovery=2,
                )
            )
            new_self = replace(new_self, usages=self.usages - 1, activated=False)

        elif signal is TriggeringSignal.ROUND_END:
            new_self = type(self)(usages=1, activated=False)

        return es, new_self

    def __str__(self) -> str:
        return super().__str__() + case_val(self.activated, "(*)", '')


#### Kamisato Ayaka ####


@dataclass(frozen=True, kw_only=True)
class KamisatoArtSenhoStatus(CharacterHiddenStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.SELF_SWAP,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.SELF_SWAP:
            assert isinstance(detail, SwapIEvent), f"{game_state}"
            if detail.target == source:
                source_char = game_state.get_character_target(source)
                assert source_char is not None
                effects: list[eft.Effect] = []
                if (
                        source_char.talent_equipped()
                        and KamisatoAyakaCryoInfusionStatus in source_char.character_statuses
                ):
                    effects.append(
                        eft.RemoveCharacterStatusEffect(
                            target=source,
                            status=KamisatoAyakaCryoInfusionStatus,
                        )
                    )
                effects.append(
                    eft.AddCharacterStatusEffect(
                        target=source,
                        status=(
                            KamisatoAyakaCryoInfusionEnhancedStatus
                            if source_char.talent_equipped()
                            else KamisatoAyakaCryoInfusionStatus
                        ),
                    )
                )
                return effects, self
        return [], self


@dataclass(frozen=True, kw_only=True)
class KamisatoAyakaCryoInfusionEnhancedStatus(CharacterStatus, _InfusionStatus):
    ELEMENT: ClassVar[Element] = Element.CRYO
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    DAMAGE_BOOST: ClassVar[int] = 1


@dataclass(frozen=True, kw_only=True)
class KamisatoAyakaCryoInfusionStatus(CharacterStatus, _InfusionStatus):
    ELEMENT: ClassVar[Element] = Element.CRYO
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1


@dataclass(frozen=True, kw_only=True)
class KantenSenmyouBlessingStatus(TalentEquipmentStatus, _UsageStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    AUTO_DESTROY: ClassVar[bool] = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import KantenSenmyouBlessing
        return KantenSenmyouBlessing

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SWAP_COST_OMNI:
            assert isinstance(item, ActionPEvent)
            if (
                    item.target == status_source
                    and item.dice_cost.can_cost_less_elem()
                    and self.usages > 0
            ):
                return (
                    item.with_new_cost(item.dice_cost.cost_less_elem(1)),
                    replace(self, usages=self.usages - 1),
                )
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


#### Keqing ####


@dataclass(frozen=True, kw_only=True)
class KeqingTalentStatus(CharacterHiddenStatus):
    can_infuse: bool
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
    ))

    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | KeqingTalentStatus]:
        if signal is TriggeringSignal.POST_SKILL:
            return [], type(self)(can_infuse=False)
        return [], self  # pragma: no cover

    def __str__(self) -> str:
        return super().__str__() + f"({case_val(self.can_infuse, 1, 0)})"  # pragma: no cover


@dataclass(frozen=True, kw_only=True)
class ThunderingPenanceStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import ThunderingPenance
        return ThunderingPenance


@dataclass(frozen=True, kw_only=True)
class KeqingElectroInfusionEnhancedStatus(CharacterStatus, _InfusionStatus):
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 3
    ELEMENT: ClassVar[Element] = Element.ELECTRO
    DAMAGE_BOOST: ClassVar[int] = 1


@dataclass(frozen=True, kw_only=True)
class KeqingElectroInfusionStatus(CharacterStatus, _InfusionStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    ELEMENT: ClassVar[Element] = Element.ELECTRO


#### Klee ####


@dataclass(frozen=True, kw_only=True)
class ExplosiveSparkStatus(CharacterStatus, _UsageStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 2
    DAMAGE_BOOST: ClassVar[int] = 1
    COST_DEDUCTION: ClassVar[int] = 1

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if status_source != dmg.source:
                return item, self
            if dmg.damage_type.direct_charged_attack():
                new_item = DmgPEvent(dmg=replace(dmg, damage=dmg.damage + self.DAMAGE_BOOST))
                new_self = replace(self, usages=self.usages - 1)
                return new_item, new_self
        elif signal is Preprocessables.SKILL_COST_ELEM:
            assert isinstance(item, ActionPEvent)
            player = game_state.get_player(status_source.pid)
            if (
                    status_source == item.source
                    and item.event_type is EventType.SKILL1
                    and player.dice.is_even()
                    and item.dice_cost.can_cost_less_elem(Element.PYRO)
            ):
                return item.with_new_cost(item.dice_cost.cost_less_elem(
                    self.COST_DEDUCTION, Element.PYRO,
                )), self
        return item, self


@dataclass(frozen=True, kw_only=True)
class PoundingSurpriseStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import PoundingSurprise
        return PoundingSurprise


@dataclass(frozen=True, kw_only=True)
class SparksnSplashStatus(CombatStatus, _UsageStatus):
    usages: int = 2
    activated: bool = False
    MAX_USAGES: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
    ))

    @override
    def _inform(
            self, game_state: GameState, status_source: StaticTarget, info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if self.activated or self.usages == 0:
            return self

        if info_type is not Informables.POST_SKILL_USAGE:
            return self

        assert isinstance(information, SkillIEvent), information
        if status_source.pid is not information.source.pid:
            return self

        return replace(self, activated=True)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        es: list[eft.Effect] = []
        new_self = self

        if signal is TriggeringSignal.POST_SKILL and self.activated:
            assert self.usages >= 1
            es.append(
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.SELF_ACTIVE,
                    element=Element.PYRO,
                    damage=2,
                    damage_type=DamageType(status=True, no_boost=True)
                )
            )
            new_self = replace(new_self, usages=-1, activated=False)

        return es, new_self


#### Kujou Sara ####


@dataclass(frozen=True, kw_only=True)
class CrowfeatherCoverStatus(CharacterStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2

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
            if not (
                    item.dmg.source == status_source
                    and (
                        item.dmg.damage_type.direct_elemental_skill()
                        or item.dmg.damage_type.direct_elemental_burst()
                    )
            ):
                return item, self
            dmg_boost = 1
            source_char = game_state.get_character_target(status_source)
            if source_char is not None and source_char.ELEMENT is Element.ELECTRO:
                dmg_boost += len([
                    char
                    for char in game_state.get_player(
                        status_source.pid
                    ).characters.get_alive_characters()
                    if SinOfPrideStatus in char.character_statuses
                ])
            return item.delta_damage(dmg_boost), replace(self, usages=self.usages - 1)
        return item, self


@dataclass(frozen=True, kw_only=True)
class SinOfPrideStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import SinOfPride
        return SinOfPride


#### Layla ####

@dataclass(frozen=True, kw_only=True)
class CurtainOfSlumberStatus(CombatStatus, StackedShieldStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2


@dataclass(frozen=True, kw_only=True)
class LightsRemitStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import LightsRemit
        return LightsRemit


@dataclass(frozen=True, kw_only=True)
class ShootingStarStatus(CombatStatus, _UsageLivingStatus):
    usages: int = 0
    used_skill: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
    ))

    @override
    def add(self, other: type[Self]) -> None | Self:
        return self.update(replace(self, usages=2))

    @override
    def _inform(
            self, game_state: GameState, status_source: StaticTarget, info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if information.source.pid == status_source.pid:
                return replace(self, used_skill=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL:
            effects: list[eft.Effect] = []
            curr_usages = self.usages
            if self.used_skill:
                effects.append(eft.UpdateCombatStatusEffect(
                    target_pid=source.pid,
                    status=ShootingStarStatus(usages=1, used_skill=False),
                ))
                curr_usages += 1
            if curr_usages >= 4:
                from ..character.character import Layla
                effects.append(eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.CRYO,
                    damage=1,
                    damage_type=DamageType(status=True),
                ))
                layla = game_state.get_player(source.pid).characters.find_first_character(Layla)
                if layla is not None and layla.talent_equipped():
                    effects.append(eft.DrawTopCardEffect(
                        pid=source.pid,
                        num=1,
                    ))
                effects.append(eft.UpdateCombatStatusEffect(
                    target_pid=source.pid,
                    status=ShootingStarStatus(usages=-4, used_skill=False),
                ))
            return effects, self
        return [], self


#### Lisa ####

@dataclass(frozen=True, kw_only=True)
class ConductiveStatus(CharacterStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 4
    REPEATED_USAGES: ClassVar[int | None] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            if self.usages < self.MAX_USAGES:
                return [], replace(self, usages=1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class PulsatingWitchStatus(TalentEquipmentStatus, _UsageLivingStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.SELF_SWAP,
        TriggeringSignal.ROUND_END,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import PulsatingWitch
        return PulsatingWitch

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.SELF_SWAP and self.usages > 0:
            if StaticTarget.from_player_active(game_state, source.pid) == source:
                return [
                    eft.RelativeAddCharacterStatusEffect(
                        source_pid=source.pid,
                        target=DynamicCharacterTarget.OPPO_ACTIVE,
                        status=ConductiveStatus,
                    )
                ], replace(self, usages=-1)
        elif signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


#### Lyney ####

@dataclass(frozen=True, kw_only=True)
class ConclusiveOvationStatus(TalentEquipmentStatus, _UsageLivingStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import ConclusiveOvation
        return ConclusiveOvation

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            if not (
                    self.usages > 0
                    and item.dmg.source.pid is status_source.pid
            ):
                return item, self
            boostable = False
            target_character = game_state.get_character_target(item.dmg.target)
            if target_character is not None and target_character.elemental_aura.contains(Element.PYRO):
                if item.dmg.damage_type.directly_from_character():
                    boostable = item.dmg.source == status_source
                elif item.dmg.damage_type.summon:
                    from ..summon.summon import GrinMalkinHatSummon
                    summon_instance = game_state.get_target(item.dmg.source)
                    boostable = isinstance(summon_instance, GrinMalkinHatSummon)
            if boostable:
                return item.delta_damage(2), replace(self, usages=-1)
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], replace(self, usages=self.MAX_USAGES)
        return [], self


@dataclass(frozen=True, kw_only=True)
class PropSurplusStatus(CharacterStatus, _UsageLivingStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 3
    triggered: bool = False  # damage boost has taken effect
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
    ))

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            if not (
                    self.usages > 0
                    and item.dmg.source == status_source
                    and item.dmg.damage_type.direct_elemental_skill()
            ):
                return item, self
            return item.delta_damage(self.usages), replace(self, triggered=True)
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.triggered:
            return [
                eft.RecoverHPEffect(
                    source=source,
                    target=source,
                    recovery=self.usages,
                ),
            ], None
        return [], self


#### Maguu Kenki ####

@dataclass(frozen=True, kw_only=True)
class TranscendentAutomatonStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import TranscendentAutomaton
        return TranscendentAutomaton


#### Mona ####


@dataclass(frozen=True, kw_only=True)
class IllusoryBubbleStatus(CombatStatus):
    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_MUL:
            assert isinstance(item, DmgPEvent)
            if (
                    item.dmg.source.pid is status_source.pid
                    and item.dmg.damage_type.directly_from_character()
            ):
                return replace(item, dmg=replace(item.dmg, damage=item.dmg.damage * 2)), None
        return super()._preprocess(game_state, status_source, item, signal)


@dataclass(frozen=True, kw_only=True)
class IllusoryTorrentStatus(CharacterHiddenStatus):
    available: bool = True
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
        if signal is Preprocessables.SWAP:
            assert isinstance(item, ActionPEvent) and item.event_type is EventType.SWAP
            if self.available \
                    and item.source == status_source \
                    and item.event_speed is EventSpeed.COMBAT_ACTION:
                return replace(
                    item, event_speed=EventSpeed.FAST_ACTION
                ), replace(self, available=False)
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        new_self = self
        if signal is TriggeringSignal.ROUND_END:
            if not self.available:
                new_self = replace(new_self, available=True)
        return [], new_self

    def __str__(self) -> str:
        return super().__str__() + f"({'*' if self.available else ''})"


@dataclass(frozen=True, kw_only=True)
class ProphecyOfSubmersionStatus(TalentEquipmentStatus):
    DMG_BOOST: ClassVar[int] = 2

    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import ProphecyOfSubmersion
        return ProphecyOfSubmersion

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
            if (
                    dmg.source.pid is status_source.pid
                    and dmg.damage_type.can_boost()
                    and dmg.reaction is not None
                    and dmg.reaction.elem_reaction(Element.HYDRO)
                    and (
                    game_state.get_player(
                            status_source.pid
                        ).just_get_active_character().id == status_source.id
                    )
            ):
                dmg = replace(dmg, damage=dmg.damage + self.DMG_BOOST)
                return DmgPEvent(dmg=dmg), self
        return super()._preprocess(game_state, status_source, item, signal)

#### Nahida ####


@dataclass(frozen=True, kw_only=True)
class SeedOfSkandhaStatus(CharacterStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_DMG,
        TriggeringSignal.DIRECT_TRIGGER,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_DMG:
            assert isinstance(detail, DmgIEvent)
            if not (
                    detail.dmg.target == source
                    and detail.dmg.reaction is not None
            ):
                return [], self
            assert self.usages > 0, f"{game_state}"
            dmg_element: Element
            oppo_player = game_state.get_player(source.pid.other)
            oppo_chars = oppo_player.characters
            from ..character.character import Nahida
            if (
                    any(char.talent_equipped() for char in oppo_chars if isinstance(char, Nahida))
                    and ShrineOfMayaStatus in oppo_player.combat_statuses
                    and any(char.ELEMENT is Element.PYRO for char in oppo_chars)
            ):
                dmg_element = Element.DENDRO
            else:
                dmg_element = Element.PIERCING
            effects: list[eft.Effect] = [
                eft.SpecificDamageEffect(
                    source=source,
                    target=source,
                    element=dmg_element,
                    damage=1,
                    damage_type=DamageType(status=True, no_boost=True),
                ),
                eft.UpdateCharacterStatusEffect(
                    target=source,
                    status=replace(self, usages=-1),
                ),
            ]
            off_field_alive_chars = game_state.get_player(
                source.pid
            ).characters.get_character_ordered_from_id(cast(int, source.id))[1:]
            for char in off_field_alive_chars:
                effects.extend((
                    eft.EffectsGroupStartEffect(),
                    eft.TriggerStatusEffect(
                        target=StaticTarget.from_char_id(source.pid, char.id),
                        status=SeedOfSkandhaStatus,
                        signal=TriggeringSignal.DIRECT_TRIGGER,
                    ),
                ))
            return effects, self
        elif signal is TriggeringSignal.DIRECT_TRIGGER:
            return [
                eft.SpecificDamageEffect(
                    source=source,
                    target=source,
                    element=Element.PIERCING,
                    damage=1,
                    damage_type=DamageType(status=True, no_boost=True),
                ),
            ], replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class ShrineOfMayaStatus(CombatStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DAMAGE_BOOST: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if not (
                    dmg.source.pid is status_source.pid
                    and dmg.damage_type.directly_from_character()
                    and dmg.reaction is not None
            ):
                return item, self
            dmg = replace(dmg, damage=dmg.damage + self.DAMAGE_BOOST)
            return DmgPEvent(dmg=dmg), self
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class TheSeedOfStoredKnowledgeStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import TheSeedOfStoredKnowledge
        return TheSeedOfStoredKnowledge


#### Ningguang ####

@dataclass(frozen=True, kw_only=True)
class JadeScreenStatus(CombatStatus, FixedShieldStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    SHIELD_AMOUNT: ClassVar[int] = 1
    DAMAGE_THRESHOLD: ClassVar[int] = 2

    @override
    def _triggering_condition(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            damage: eft.SpecificDamageEffect
    ) -> bool:
        return damage.damage >= self.DAMAGE_THRESHOLD

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
                    item.dmg.element is Element.GEO
                    and item.dmg.source.pid is status_source.pid
                    and item.dmg.damage_type.can_boost()
            ):
                active_char = game_state.get_player(status_source.pid).just_get_active_character()
                from ..character.character import Ningguang
                if isinstance(active_char, Ningguang) and active_char.talent_equipped():
                    return item.delta_damage(1), self
        return super()._preprocess(game_state, status_source, item, signal)


@dataclass(frozen=True, kw_only=True)
class StrategicReserveStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import StrategicReserve
        return StrategicReserve


#### Noelle ####

@dataclass(frozen=True, kw_only=True)
class FullPlateStatus(CombatStatus, StackedShieldStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    heal_usages: int = 1
    MAX_HEAL_USAGES: ClassVar[int] = 1
    HEAL_AMOUNT: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
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
        if signal is Preprocessables.DMG_AMOUNT_MUL:
            assert isinstance(item, DmgPEvent)
            if (
                    item.dmg.element is Element.PHYSICAL
                    and self._target_is_self_active(game_state, status_source, item.dmg.target)
            ):
                from math import ceil
                return replace(item, dmg=replace(item.dmg, damage=ceil(item.dmg.damage / 2))), self
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL:
            if self.heal_usages <= 0:
                return [], self
            this_player = game_state.get_player(source.pid)
            char_self = this_player.just_get_active_character()
            if not char_self.talent_equipped():
                return [], self
            effects: list[eft.Effect] = []
            for char in this_player.characters.get_character_in_activity_order():
                if char.is_alive():
                    effects.append(eft.RecoverHPEffect(
                        source=source,
                        target=StaticTarget(source.pid, Zone.CHARACTERS, char.id),
                        recovery=self.HEAL_AMOUNT,
                    ))
            return effects, replace(self, usages=0, heal_usages=self.heal_usages - 1)
        elif signal is TriggeringSignal.ROUND_END:
            if self.heal_usages < self.MAX_HEAL_USAGES:
                return [], replace(self, heal_usages=self.MAX_HEAL_USAGES)
        return [], self


@dataclass(frozen=True, kw_only=True)
class IGotYourBackStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import IGotYourBack
        return IGotYourBack


@dataclass(frozen=True, kw_only=True)
class SweepingTimeStatus(CharacterStatus, _InfusionStatus):
    usages: int = 2  # duration
    ELEMENT: ClassVar[Element] = Element.GEO
    DAMAGE_BOOST: ClassVar[int] = 2
    dice_reduction_usages: int = 1
    DICE_REDUCTION: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _dmg_boost_condition(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: eft.SpecificDamageEffect,
    ) -> bool:
        return (
            super()._dmg_boost_condition(game_state, status_source, item)
            and item.damage_type.direct_normal_attack()
        )

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SKILL_COST_ELEM:
            assert isinstance(item, ActionPEvent)
            if (
                    self.dice_reduction_usages > 0
                    and status_source == item.source
                    and item.event_type is EventType.SKILL1
                    and item.dice_cost.can_cost_less_elem(Element.GEO)
            ):
                return item.with_new_cost(
                    item.dice_cost.cost_less_elem(self.DICE_REDUCTION, Element.GEO)
                ), replace(self, dice_reduction_usages=self.dice_reduction_usages - 1)
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-1, dice_reduction_usages=1)
        return [], self

    def __str__(self) -> str:
        return super().__str__() + f"({self.dice_reduction_usages})"


#### Qiqi ####

@dataclass(frozen=True, kw_only=True)
class FortunePreservingTalismanStatus(CombatStatus, _UsageStatus):
    """
    Tested, Qiqi's burst doesn't trigger this status
    """
    usages: int = 3
    activated: bool = False
    MAX_USAGES: ClassVar[int] = 3
    HEAL_AMOUNT: ClassVar[int] = 2

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
            from ..character.character import Qiqi
            if (
                    not self.activated
                    and information.is_skill_from_character(game_state, status_source.pid)
                    and not information.is_skill_from_character(
                        game_state,
                        status_source.pid,
                        CharacterSkill.ELEMENTAL_BURST,
                        Qiqi,
                    )
            ):
                return replace(self, activated=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.activated:
            active_char = game_state.get_player(source.pid).just_get_active_character()
            if active_char.hp_lost() == 0:
                return [], replace(self, usages=0, activated=False)
            return [
                eft.RecoverHPEffect(
                    source=source,
                    target=StaticTarget.from_char_id(source.pid, active_char.id),
                    recovery=self.HEAL_AMOUNT,
                )
            ], replace(self, usages=-1, activated=False)
        return [], self


@dataclass(frozen=True, kw_only=True)
class QiqiTalentStatus(CharacterHiddenStatus):
    revival_count: int = 0
    MAX_COUNT: ClassVar[int] = 2

    def revivable(self) -> bool:
        return self.revival_count < self.MAX_COUNT

    def __str__(self) -> str:
        return super().__str__() + f"({self.revival_count})"


@dataclass(frozen=True, kw_only=True)
class RiteOfResurrectionStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import RiteOfResurrection
        return RiteOfResurrection


#### Raiden Shogun ####


@dataclass(frozen=True, kw_only=True)
class ChakraDesiderataHiddenStatus(CharacterHiddenStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.INIT_GAME_START,
        TriggeringSignal.REVIVAL_GAME_START,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal in (TriggeringSignal.INIT_GAME_START, TriggeringSignal.REVIVAL_GAME_START):
            return [
                eft.AddCharacterStatusEffect(
                    target=source,
                    status=ChakraDesiderataStatus,
                ),
            ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class ChakraDesiderataStatus(CharacterStatus, _UsageLivingStatus):
    usages: int = 0
    MAX_USAGES: ClassVar[int] = 3

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
            if (
                    information.source.pid is status_source.pid
                    and information.source.id != status_source.id
                    and information.skill_true_type is CharacterSkillType.ELEMENTAL_BURST
                    and self.usages < self.MAX_USAGES
            ):
                return replace(self, usages=self.usages + 1)
        return self

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
                    item.dmg.source == status_source
                    and item.dmg.damage_type.direct_elemental_burst()
                    and self.usages > 0
            ):
                this_char = game_state.get_character_target(status_source)
                assert this_char is not None
                if this_char.talent_equipped():
                    return item.delta_damage(2 * self.usages), replace(self, usages=0)
                else:
                    return item.delta_damage(self.usages), replace(self, usages=0)
        return item, self


@dataclass(frozen=True, kw_only=True)
class WishesUnnumberedStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import WishesUnnumbered
        return WishesUnnumbered


#### Rhodeia of Loch ####


@dataclass(frozen=True, kw_only=True)
class StreamingSurgeStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import StreamingSurge
        return StreamingSurge


#### Sangonomiya Kokomi ####

@dataclass(frozen=True, kw_only=True)
class CeremonialGarmentStatus(CharacterStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DAMAGE_BOOST: ClassVar[int] = 1
    activated: bool = False

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
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
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (
                    dmg.source == status_source
                    and dmg.damage_type.direct_normal_attack()
            ):
                return item.delta_damage(self.DAMAGE_BOOST), replace(self, activated=True)
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.activated:
            self_chars = game_state.get_player(source.pid).characters
            return [
                eft.RecoverHPEffect(
                    source=source,
                    target=StaticTarget.from_char_id(source.pid, char.id),
                    recovery=1,
                )
                for char in self_chars.get_alive_character_in_activity_order()
            ], replace(self, usages=0, activated=False)
        elif signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class TamakushiCasketStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import TamakushiCasket
        return TamakushiCasket


#### Shenhe ####


@dataclass(frozen=True, kw_only=True)
class IcyQuillStatus(CombatStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 3
    DMG_BOOST: ClassVar[int] = 1
    normal_attack_deduction_usages: int = 1
    DEFAULT_NORMAL_ATTACK_DEDUCTION_USAGES: ClassVar[int] = 1

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if not (
                    dmg.source.pid is status_source.pid
                    and dmg.element is Element.CRYO
                    and dmg.damage_type.from_character()
            ):
                return item, self
            dmg = replace(dmg, damage=dmg.damage + self.DMG_BOOST)
            from ..character.character import Shenhe
            new_self = self
            if (
                self.normal_attack_deduction_usages > 0
                and any(
                    char.talent_equipped()
                    for char in game_state.get_player(status_source.pid).characters
                    if isinstance(char, Shenhe)
                )
                and dmg.damage_type.direct_normal_attack()
            ):
                # if talent equipped and triggered
                d_usages = 0
                new_self = replace(
                    new_self,
                    normal_attack_deduction_usages=self.normal_attack_deduction_usages - 1,
                )
            else:
                new_self = replace(new_self, usages=self.usages - 1)
            return DmgPEvent(dmg=dmg), new_self
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            if self.normal_attack_deduction_usages < self.DEFAULT_NORMAL_ATTACK_DEDUCTION_USAGES:
                return [], replace(
                    self,
                    usages=0,
                    normal_attack_deduction_usages=self.DEFAULT_NORMAL_ATTACK_DEDUCTION_USAGES,
                )
        return [], self


@dataclass(frozen=True, kw_only=True)
class MysticalAbandonStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import MysticalAbandon
        return MysticalAbandon


#### Stonehide Lawachurl ####

@dataclass(frozen=True, kw_only=True)
class StoneForceStatus(CharacterStatus):
    boostable: bool = True  # +1 DMG per round
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_STATUS_REMOVAL,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS and self.boostable:
            assert isinstance(item, DmgPEvent)
            if not (
                    item.dmg.source == status_source
                    and item.dmg.damage_type.directly_from_character()
            ):
                return item, self
            return item.delta_damage(1), replace(self, boostable=False)
        elif signal is Preprocessables.DMG_ELEMENT and self.boostable:
            assert isinstance(item, DmgPEvent)
            if not (
                    item.dmg.source == status_source
                    and item.dmg.damage_type.directly_from_character()
            ):
                return item, self
            if item.dmg.element is Element.PHYSICAL:
                return item.convert_element(Element.GEO), self
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_STATUS_REMOVAL:
            assert isinstance(detail, StatusRemovalIEvent)
            if detail.status is StonehideStatus and detail.target == source:
                return [], None
        elif signal is TriggeringSignal.ROUND_END and not self.boostable:
            return [], replace(self, boostable=True)
        return [], self


@dataclass(frozen=True, kw_only=True)
class StonehideReforgedStatus(TalentEquipmentStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_DMG,
    ))

    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import StonehideReforged
        return StonehideReforged

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_DMG:
            assert isinstance(detail, DmgIEvent)
            if (
                    detail.lethal
                    and detail.dmg.source == source
                    and detail.dmg.damage_type.directly_from_character()
                    and detail.dmg.target.pid is source.pid.other
            ):
                return [
                    eft.AddCharacterStatusEffect(source, StonehideStatus),
                    eft.AddCharacterStatusEffect(source, StoneForceStatus),
                ], self
        return [], self


@dataclass(frozen=True, kw_only=True)
class StonehideStatus(CharacterStatus, FixedShieldStatus):
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 3
    SHIELD_AMOUNT: ClassVar[int] = 1


#### Tartaglia ####

@dataclass(frozen=True, kw_only=True)
class AbyssalMayhemHydrospoutStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import AbyssalMayhemHydrospout
        return AbyssalMayhemHydrospout


@dataclass(frozen=True, kw_only=True)
class MeleeStanceStatus(CharacterStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2

    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.ROUND_END,
    })

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            oppo_char = game_state.get_character_target(dmg.target)
            assert oppo_char is not None
            if (
                    dmg.source == status_source
                    and dmg.damage_type.directly_from_character()
                    and RiptideStatus in oppo_char.character_statuses
            ):
                return item.delta_damage(1), self
        elif signal is Preprocessables.DMG_ELEMENT:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if (dmg.source == status_source and dmg.element is Element.PHYSICAL):
                return item.convert_element(Element.HYDRO), self
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            effects: list[eft.Effect] = []
            if self.usages == 1:
                effects.append(
                    eft.AddCharacterStatusEffect(
                        target=source,
                        status=RangeStanceStatus,
                    )
                )
            return effects, type(self)(usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class RangeStanceStatus(CharacterStatus):
    pass


@dataclass(frozen=True, kw_only=True)
class RiptideCounterStatus(CharacterHiddenStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    AUTO_DESTROY: ClassVar[bool] = False

    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.ROUND_END,
    })

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END and self.usages < self.MAX_USAGES:
            return [], type(self)()
        return [], self


@dataclass(frozen=True, kw_only=True)
class RiptideTransferStatus(CombatStatus):
    """ The intermediate status to add RiptideStatus to the next active character. """
    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.SELF_SWAP,
    })

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.SELF_SWAP:  # TODO: not necessarily accurate signal
            target = StaticTarget.from_player_active(game_state, source.pid)
            return [
                eft.AddCharacterStatusEffect(
                    target=target,
                    status=RiptideStatus,
                ),
            ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class RiptideStatus(CharacterStatus):
    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.POST_DMG,
        TriggeringSignal.END_ROUND_CHECK_OUT,
    })

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_DMG:
            assert isinstance(detail, DmgIEvent)
            if (
                    detail.lethal
                    and detail.dmg.target == source
            ):
                self_active = game_state.get_player(source.pid).just_get_active_character()
                if self_active.alive:
                    return [
                        eft.AddCharacterStatusEffect(
                            target=StaticTarget.from_char_id(source.pid, self_active.id),
                            status=RiptideStatus,
                        ),
                    ], None
                return [
                    eft.AddCombatStatusEffect(source.pid, RiptideTransferStatus),
                ], None
        elif signal is TriggeringSignal.END_ROUND_CHECK_OUT:
            self_active_id = game_state.get_player(source.pid).just_get_active_character().id
            oppo_active = game_state.get_player(source.pid.other).just_get_active_character()
            if (
                    self_active_id == source.id
                    and AbyssalMayhemHydrospoutStatus in oppo_active.character_statuses
            ):
                return [
                    eft.SpecificDamageEffect(
                        source=StaticTarget.from_char_id(source.pid.other, oppo_active.id),
                        target=source,
                        element=Element.PIERCING,
                        damage=1,
                        damage_type=DamageType(status=True, no_boost=True),
                    ),
                ], self
        return [], self


@dataclass(frozen=True, kw_only=True)
class TideWithholderStatus(CharacterHiddenStatus):
    REACTABLE_SIGNALS = frozenset({
        TriggeringSignal.INIT_GAME_START,
        TriggeringSignal.REVIVAL_GAME_START,
    })

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if (
                signal is TriggeringSignal.INIT_GAME_START
                or signal is TriggeringSignal.REVIVAL_GAME_START
        ):
            return [
                eft.AddCharacterStatusEffect(
                    target=source,
                    status=RangeStanceStatus,
                ),
                eft.AddCharacterStatusEffect(
                    target=source,
                    status=RiptideCounterStatus,
                ),
            ], None
        return [], self


#### Tighnari ####


@dataclass(frozen=True, kw_only=True)
class KeenSightStatus(TalentEquipmentStatus):
    COST_DEDUCTION: ClassVar[int] = 1

    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import KeenSight
        return KeenSight

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SKILL_COST_ANY:
            assert isinstance(item, ActionPEvent)
            player = game_state.get_player(status_source.pid)
            characters = player.characters
            if (
                    status_source == item.source
                    and item.event_sub_type is CharacterSkillType.NORMAL_ATTACK
                    and player.dice.is_even()
                    and characters.just_get_character(
                        cast(int, status_source.id)
                    ).character_statuses.contains(VijnanaSuffusionStatus)
                    and item.dice_cost.can_cost_less_any()
            ):
                return item.with_new_cost(
                    item.dice_cost.cost_less_any(self.COST_DEDUCTION)
                ), self
        return super()._preprocess(game_state, status_source, item, signal)


@dataclass(frozen=True, kw_only=True)
class VijnanaSuffusionStatus(CharacterStatus, _UsageStatus):
    usages: int = 2
    activated: bool = False
    MAX_USAGES: ClassVar[int] = 2
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
        if (
                self.activated
                or self.usages == 0
                or not isinstance(information, DmgIEvent)
                or status_source != information.dmg.source
                or not information.dmg.damage_type.direct_charged_attack()
        ):
            return self

        return replace(self, activated=True)

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        new_item: None | DmgPEvent = None
        if signal is Preprocessables.DMG_ELEMENT:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if status_source != dmg.source:
                return item, self
            if dmg.damage_type.direct_charged_attack():
                new_item = DmgPEvent(dmg=replace(dmg, element=Element.DENDRO))
        if new_item is not None:
            return new_item, self
        else:
            return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        es: list[eft.Effect] = []
        new_self = self

        if signal is TriggeringSignal.POST_SKILL and self.activated:
            from ..summon.summon import ClusterbloomArrowSummon
            assert self.usages >= 1
            es.append(
                eft.AddSummonEffect(
                    target_pid=source.pid,
                    summon=ClusterbloomArrowSummon,
                )
            )
            new_self = replace(new_self, usages=-1, activated=False)

        return es, new_self

    @override
    def _update(self, other: Self) -> None | Self:
        new_usages = min(self.usages + other.usages, self.MAX_USAGES)
        return type(self)(
            usages=new_usages,
            activated=other.activated,
        )

    def __str__(self) -> str:
        return super().__str__() + f"({self.usages}{case_val(self.activated, '*', '')})"

#### Venti ####


@dataclass(frozen=True, kw_only=True)
class EmbraceOfWindsStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import EmbraceOfWinds
        return EmbraceOfWinds


@dataclass(frozen=True, kw_only=True)
class StormzoneStatus(CombatStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    triggered: bool = False
    COST_DEDUCTION: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.SELF_SWAP,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SWAP_COST_OMNI:
            assert isinstance(item, ActionPEvent) and item.event_type is EventType.SWAP
            if item.source.pid is status_source.pid \
                    and item.dice_cost.num_dice() >= self.COST_DEDUCTION:
                assert not self.triggered
                new_cost = item.dice_cost.cost_less_elem(self.COST_DEDUCTION)
                return item.with_new_cost(new_cost), replace(self, triggered=True)
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if self.triggered and signal is TriggeringSignal.SELF_SWAP:
            from ..character.character import Venti
            has_talent = any(
                char.talent_equipped()
                for char in game_state.get_player(source.pid).characters
                if isinstance(char, Venti)
            )
            effects: list[eft.Effect] = []
            if has_talent:
                effects.append(eft.AddCombatStatusEffect(
                    target_pid=source.pid,
                    status=WindsOfHarmonyStatus,
                ))
            return effects, replace(self, usages=-1, triggered=False)
        return [], self


@dataclass(frozen=True, kw_only=True)
class WindsOfHarmonyStatus(CombatStatus):
    COST_DEDUCTION: ClassVar[int] = 1
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SKILL_COST_ANY:
            assert isinstance(item, ActionPEvent)
            if status_source.pid is item.source.pid \
                    and item.event_sub_type is CharacterSkillType.NORMAL_ATTACK \
                    and item.dice_cost[Element.ANY] >= self.COST_DEDUCTION:
                return item.with_new_cost(
                    item.dice_cost.cost_less_any(self.COST_DEDUCTION)
                ), None
        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self

#### Wanderer ####


@dataclass(frozen=True, kw_only=True)
class DescentStatus(CharacterStatus):
    activated: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.SELF_SWAP,
    ))

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.SWAP_COST_OMNI:
            assert isinstance(item, ActionPEvent) and item.event_type is EventType.SWAP
            if item.source == status_source and item.dice_cost.can_cost_less_elem():
                return (
                    item.with_new_cost(item.dice_cost.cost_less_elem(1)),
                    replace(self, activated=True),
                )
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.SELF_SWAP and self.activated:
            return [
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.ANEMO,
                    damage=1,
                    damage_type=DamageType(status=True),
                )
            ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class GalesOfReverieStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import GalesOfReverie
        return GalesOfReverie


@dataclass(frozen=True, kw_only=True)
class WindfavoredStatus(CharacterStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2

    @override
    def _preprocess(
            self,
            game_state: GameState,
            status_source: StaticTarget,
            item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_ELEMENT:
            assert isinstance(item, DmgPEvent)
            if not (
                    item.dmg.source == status_source
                    and item.dmg.damage_type.direct_normal_attack()
            ):
                return item, self
            oppo_player = game_state.get_player(status_source.pid.other)
            alive_chars = oppo_player.characters.get_alive_character_in_activity_order()
            if len(alive_chars) > 1:
                return (
                    item.change_target(StaticTarget.from_char_id(
                        status_source.pid.other,
                        alive_chars[1].id,
                    )),
                    self,
                )
        elif signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            if not (
                    item.dmg.source == status_source
                    and item.dmg.damage_type.direct_normal_attack()
            ):
                return item, self
            return item.delta_damage(2), replace(self, usages=self.usages - 1)
        return item, self


#### Xiangling ####

@dataclass(frozen=True, kw_only=True)
class PyronadoStatus(CombatStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    DMG_AMOUNT: ClassVar[int] = 2
    DMG_ELEM: ClassVar[Element] = Element.PYRO

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL:
            assert isinstance(detail, SkillIEvent)
            if detail.source.pid is source.pid:
                return [eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=self.DMG_ELEM,
                    damage=self.DMG_AMOUNT,
                    damage_type=DamageType(status=True),
                )], replace(self, usages=-1)
        return [], self


#### Xingqiu ####


@dataclass(frozen=True, kw_only=True)
class RainSwordStatus(CombatStatus, FixedShieldStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    SHIELD_AMOUNT: ClassVar[int] = 1
    DAMAGE_THRESHOLD: ClassVar[int] = 3
    TALENT_DMG_THRESHOLD: ClassVar[int] = 2

    @override
    def _triggering_condition(
            self, game_state: GameState, status_source: StaticTarget,
            damage: eft.SpecificDamageEffect
    ) -> bool:
        from ..character.character import Xingqiu
        talent_equipped = any(
            True
            for char in game_state.get_player(status_source.pid).characters
            if (
                isinstance(char, Xingqiu)
                and char.talent_equipped()
            )
        )
        return damage.damage >= (
            self.TALENT_DMG_THRESHOLD if talent_equipped else self.DAMAGE_THRESHOLD
        )


@dataclass(frozen=True, kw_only=True)
class RainbowBladeworkStatus(CombatStatus, _UsageStatus):
    activated: bool = False
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 3
    DAMAGE: ClassVar[int] = 1
    ELEMENT: ClassVar[Element] = Element.HYDRO

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
    ))

    @override
    def _inform(
            self, game_state: GameState, status_source: StaticTarget, info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if (
                not isinstance(information, SkillIEvent)
                or information.skill_true_type is not CharacterSkillType.NORMAL_ATTACK
                or status_source.pid is not information.source.pid
        ):
            return self

        return replace(self, activated=True)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.activated:
            assert self.usages >= 1
            return [
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=self.ELEMENT,
                    damage=self.DAMAGE,
                    damage_type=DamageType(status=True),
                )
            ], replace(self, usages=-1, activated=False)
        return [], self


@dataclass(frozen=True, kw_only=True)
class TheScentRemainedStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import TheScentRemained
        return TheScentRemained

#### Yae Miko ####


@dataclass(frozen=True, kw_only=True)
class RiteOfDispatchStatus(CharacterStatus):
    COST_DEDUCTION: ClassVar[int] = 2

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
        """
        The assumption here is the equiper only pay elemental skill with electro or omni dice
        """
        if signal is Preprocessables.SKILL_COST_ELEM:
            assert isinstance(item, ActionPEvent)
            if (
                    status_source == item.source
                    and item.event_type is EventType.SKILL2
                    and item.dice_cost.num_dice() > 0
            ):
                return item.with_new_cost(
                    item.dice_cost.cost_less_elem(self.COST_DEDUCTION, Element.ELECTRO)
                ), None
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.ROUND_END:
            return [], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class TenkoThunderboltsStatus(CombatStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.PRE_ACTION,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.PRE_ACTION:
            if game_state.active_player_id is source.pid:
                return [
                    eft.ReferredDamageEffect(
                        source=source,
                        target=DynamicCharacterTarget.OPPO_ACTIVE,
                        element=Element.ELECTRO,
                        damage=3,
                        damage_type=DamageType(status=True),
                    ),
                ], None
        return [], self


@dataclass(frozen=True, kw_only=True)
class TheShrinesSacredShadeStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import TheShrinesSacredShade
        return TheShrinesSacredShade


#### Yaoyao ####

@dataclass(frozen=True, kw_only=True)
class AdeptalLegacyStatus(CombatStatus, _UsageStatus):
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 3
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.SELF_SWAP,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.SELF_SWAP:
            return [
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.DENDRO,
                    damage=1,
                    damage_type=DamageType(status=True),
                ),
                eft.RecoverHPEffect(
                    source=source,
                    target=StaticTarget.from_player_active(game_state, source.pid),
                    recovery=1,
                ),
            ], replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class BeneficentStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import Beneficent
        return Beneficent


#### Yelan ####

@dataclass(frozen=True, kw_only=True)
class BreakthroughStatus(CharacterStatus, _UsageLivingStatus):
    usages: int = 1
    MAX_USAGES: ClassVar[int] = 3
    should_draw: bool = False
    should_stack: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
    ))

    @override
    def _inform(
            self, game_state: GameState, status_source: StaticTarget, info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if (
                    self.usages < self.MAX_USAGES
                    and information.source == status_source
                    and information.skill_type is CharacterSkill.SKILL2
            ):
                return replace(self, should_stack=True)
        return self

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_ELEMENT:
            assert isinstance(item, DmgPEvent)
            if (
                    self.usages >= 2
                    and item.dmg.source == status_source
                    and item.dmg.element is Element.PHYSICAL
                    and item.dmg.damage_type.direct_normal_attack()
            ):
                return (
                    item.convert_element(Element.HYDRO),
                    replace(self, should_draw=True),
                )
        return item, self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL:
            if self.should_draw:
                return [
                    eft.DrawTopCardEffect(pid=source.pid, num=1),
                ], replace(self, usages=-2, should_draw=False)
            elif self.should_stack:
                return [], replace(self, usages=2, should_stack=False)
        return [], self


@dataclass(frozen=True, kw_only=True)
class ExquisiteThrowStatus(CombatStatus, _UsageStatus):
    usages: int = 2
    MAX_USAGES: ClassVar[int] = 2
    normal_attacked: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
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
            if (
                    information.source.pid is status_source.pid
                    and information.skill_true_type is CharacterSkillType.NORMAL_ATTACK
            ):
                return replace(self, normal_attacked=True)
        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.normal_attacked:
            return [
                eft.ReferredDamageEffect(
                    source=source,
                    target=DynamicCharacterTarget.OPPO_ACTIVE,
                    element=Element.HYDRO,
                    damage=1,
                    damage_type=DamageType(status=True),
                ),
            ], replace(self, normal_attacked=False)
        elif signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-1)
        return [], self


@dataclass(frozen=True, kw_only=True)
class TurnControlStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import TurnControl
        return TurnControl

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.ROLL_DICE_INIT:
            assert isinstance(item, DiceRollInitPEvent)
            if (
                    item.pid == status_source.pid
                    and item.can_update()
            ):
                char_unique_elems = {
                    char.ELEMENT
                    for char in game_state.get_player(status_source.pid).characters
                }
                return item.update(Element.OMNI, len(char_unique_elems)), self
        return super()._preprocess(game_state, status_source, item, signal)


@dataclass(frozen=True, kw_only=True)
class YelanPassiveStatus(CharacterHiddenStatus):
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.INIT_GAME_START,
        TriggeringSignal.REVIVAL_GAME_START,
        TriggeringSignal.END_ROUND_CHECK_OUT,
    ))

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal in {
                TriggeringSignal.INIT_GAME_START,
                TriggeringSignal.REVIVAL_GAME_START,
                TriggeringSignal.END_ROUND_CHECK_OUT,
        }:
            return [
                eft.AddCharacterStatusEffect(
                    target=source,
                    status=BreakthroughStatus,
                )
            ], self
        return [], self


#### Yoimiya ####

@dataclass(frozen=True, kw_only=True)
class AurousBlazeStatus(CombatStatus, _UsageStatus):
    usages: int = 2  # duration
    MAX_USAGES: ClassVar[int] = 2
    activated: bool = False
    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
        TriggeringSignal.ROUND_END,
    ))

    @override
    def _inform(
            self, game_state: GameState, status_source: StaticTarget, info_type: Informables,
            information: InformableEvent,
    ) -> Self:
        if self.activated:
            return self

        if info_type is Informables.POST_SKILL_USAGE:
            assert isinstance(information, SkillIEvent)
            if status_source.pid is not information.source.pid:
                return self
            source_char = game_state.get_character_target(information.source)
            assert source_char is not None
            from ..character.character import Yoimiya
            if isinstance(source_char, Yoimiya):
                return self
            return replace(self, activated=True)

        return self

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL and self.activated:
            assert self.usages >= 1
            return [eft.ReferredDamageEffect(
                source=source,
                target=DynamicCharacterTarget.OPPO_ACTIVE,
                element=Element.PYRO,
                damage=1,
                damage_type=DamageType(status=True),
            )], replace(self, usages=0, activated=False)

        elif signal is TriggeringSignal.ROUND_END:
            return [], replace(self, usages=-1)

        return [], self


@dataclass(frozen=True, kw_only=True)
class NaganoharaMeteorSwarmStatus(TalentEquipmentStatus):
    @cached_classproperty
    def CARD(cls) -> type[crd.TalentEquipmentCard]:
        from ..card.card import NaganoharaMeteorSwarm
        return NaganoharaMeteorSwarm


@dataclass(frozen=True, kw_only=True)
class NiwabiEnshouStatus(CharacterStatus, _UsageStatus):
    usages: int = 3
    MAX_USAGES: ClassVar[int] = 3
    activated: bool = False
    DAMAGE_BOOST: ClassVar[int] = 1
    INFUSION_ELEMENT: ClassVar[Element] = Element.PYRO

    REACTABLE_SIGNALS: ClassVar[frozenset[TriggeringSignal]] = frozenset((
        TriggeringSignal.POST_SKILL,
    ))

    @override
    def _preprocess(
            self, game_state: GameState, status_source: StaticTarget, item: PreprocessableEvent,
            signal: Preprocessables,
    ) -> tuple[PreprocessableEvent, None | Self]:
        if signal is Preprocessables.DMG_AMOUNT_PLUS:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if dmg.source == status_source and dmg.damage_type.direct_normal_attack():
                return item.delta_damage(self.DAMAGE_BOOST), (
                    self
                    if self.activated
                    else replace(self, activated=True)
                )
        elif signal is Preprocessables.DMG_ELEMENT:
            assert isinstance(item, DmgPEvent)
            dmg = item.dmg
            if not (
                    dmg.source == status_source
                    and dmg.element is Element.PHYSICAL
                    and dmg.damage_type.directly_from_character()
            ):
                return item, self
            return item.convert_element(self.INFUSION_ELEMENT), (
                self
                if self.activated
                else replace(self, activated=True)
            )

        return super()._preprocess(game_state, status_source, item, signal)

    @override
    def _react_to_signal(
            self, game_state: GameState, source: StaticTarget, signal: TriggeringSignal,
            detail: None | InformableEvent
    ) -> tuple[list[eft.Effect], None | Self]:
        if signal is TriggeringSignal.POST_SKILL:
            if self.activated:
                this_char = game_state.get_character_target(source)
                assert this_char is not None
                return (
                    []
                    if not this_char.talent_equipped()
                    else [eft.ReferredDamageEffect(
                        source=source,
                        target=DynamicCharacterTarget.OPPO_ACTIVE,
                        element=Element.PYRO,
                        damage=1,
                        damage_type=DamageType(status=True),
                    )]
                ), replace(self, usages=-1, activated=False)
        return [], self
