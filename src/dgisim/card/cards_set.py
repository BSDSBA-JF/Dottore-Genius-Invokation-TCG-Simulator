from .card import *

__all__ = [
    "default_cards",
]

_DEFAULT_CARDS: list[type[Card]] = [
    # Equipment Card
    ## Talents ##
    AbsorbingPrism,
    AbyssalMayhemHydrospout,
    AratakiIchiban,
    Beneficent,
    CicinsColdGlare,
    ColdBloodedStrike,
    ConclusiveOvation,
    DescentOfDivinity,
    EmbraceOfWinds,
    FloralSidewinder,
    GalesOfReverie,
    GrandExpectation,
    IGotYourBack,
    KantenSenmyouBlessing,
    KeenSight,
    LandsOfDandelion,
    LightsRemit,
    MysticalAbandon,
    NaganoharaMeteorSwarm,
    PaidInFull,
    PoeticsOfFuubutsu,
    PoundingSurprise,
    ProliferatingSpores,
    ProphecyOfSubmersion,
    PulsatingWitch,
    RiteOfResurrection,
    SanguineRouge,
    ShakenNotPurred,
    SinOfPride,
    StalwartAndTrue,
    SteadyBreathing,
    StellarPredator,
    StonehideReforged,
    StrategicReserve,
    StreamingSurge,
    SunyataFlower,
    TamakushiCasket,
    TheScentRemained,
    TheSeedOfStoredKnowledge,
    TheShrinesSacredShade,
    ThunderingPenance,
    TranscendentAutomaton,
    TurnControl,
    UndividedHeart,
    WellspingOfWarLust,
    WishesUnnumbered,
    ## Weapons ##
    ### Bow ###
    AmosBow,
    ElegyForTheEnd,
    KingsSquire,
    RavenBow,
    SacrificialBow,
    ### Catalyst ###
    AThousandFloatingDreams,
    FruitOfFulfillment,
    MagicGuide,
    SacrificialFragments,
    ### Claymore ###
    SacrificialGreatsword,
    TheBell,
    WhiteIronGreatsword,
    WolfsGravestone,
    ### Polearm ###
    EngulfingLightning,
    LithicSpear,
    Moonpiercer,
    VortexVanquisher,
    WhiteTassel,
    ### Sword ###
    AquilaFavonia,
    FavoniusSword,
    SacrificialSword,
    TravelersHandySword,
    ## Artifact ##
    ArchaicPetra,
    BlizzardStrayer,
    BrokenRimesEcho,
    CrimsonWitchOfFlames,
    CrownOfWatatsumi,
    DeepwoodMemories,
    EchoesOfAnOffering,
    EmblemOfSeveredFate,
    ExilesCirclet,
    FlowingRings,
    GamblersEarrings,
    GeneralsAncientHelm,
    GildedDreams,
    HeartOfDepth,
    HeartOfKhvarenasBrilliance,
    InstructorsCap,
    LaurelCoronet,
    MaskOfSolitudeBasalt,
    OceanHuedClam,
    OrnateKabuto,
    ShadowOfTheSandKing,
    TenacityOfTheMillelith,
    ThunderSummonersCrown,
    ThunderingFury,
    ViridescentVenerer,
    ViridescentVenerersDiadem,
    VourukashasGlow,
    WineStainedTricorne,
    WitchsScorchingHat,

    # Event Card
    AbyssalSummons,
    BlessingOfTheDivineRelicsInstallation,
    CalxsArts,
    ChangingShifts,
    ElementalResonanceEnduringRock,
    ElementalResonanceFerventFlames,
    ElementalResonanceHighVoltage,
    ElementalResonanceImpetuousWinds,
    ElementalResonanceShatteringIce,
    ElementalResonanceSoothingWater,
    ElementalResonanceSprawlingGreenery,
    ElementalResonanceWovenFlames,
    ElementalResonanceWovenIce,
    ElementalResonanceWovenStone,
    ElementalResonanceWovenThunder,
    ElementalResonanceWovenWaters,
    ElementalResonanceWovenWeeds,
    ElementalResonanceWovenWinds,
    GuardiansOath,
    HeavyStrike,
    IHaventLostYet,
    LeaveItToMe,
    Lyresong,
    MasterOfWeaponry,
    NatureAndWisdom,
    QuickKnit,
    SendOff,
    Starsigns,
    StoneAndContracts,
    Strategize,
    TheBestestTravelCompanion,
    TheBoarPrincess,
    ThunderAndEternity,
    TossUp,
    WhenTheCraneReturned,
    WhereIsTheUnseenRazor,
    WindAndFreedom,

    ## Event Card / Arcane Legend ##
    AncientCourtyard,
    CovenantOfRock,
    FreshWindOfFreedom,
    InEveryHouseAStove,
    JoyousCelebration,
    PassingOfJudgment,

    ## Event Card / Food ##
    AdeptusTemptation,
    ButterCrab,
    JueyunGuoba,
    LotusFlowerCrisp,
    MondstadtHashBrown,
    MushroomPizza,
    MintyMeatRolls,
    NorthernSmokedChicken,
    SweetMadame,
    TandooriRoastChicken,
    TeyvatFriedEgg,

    # Support Card
    ## Support Card / Companion ##
    ChangTheNinth,
    ChefMao,
    Dunyarzad,
    Jeht,
    Liben,
    LiuSu,
    Mamere,
    MasterZhang,
    Paimon,
    Rana,
    Setaria,
    Timaeus,
    Timmie,
    Wagner,
    Xudong,
    YayoiNanatsuki,
    ## Support Card / Item ##
    MementoLens,
    NRE,
    ParametricTransformer,
    RedFeatherFan,
    SeedDispensary,
    TreasureSeekingSeelie,
    ## Support Card / Location ##
    DawnWinery,
    GandharvaVille,
    GoldenHouse,
    JadeChamber,
    KnightsOfFavoniusLibrary,
    LiyueHarborWharf,
    OperaEpiclese,
    StormterrorsLair,
    SumeruCity,
    Tenshukaku,
    Vanarana,
]

_DEFAULT_CARDS_FSET = None


def default_cards() -> frozenset[type[Card]]:
    global _DEFAULT_CARDS_FSET
    if _DEFAULT_CARDS_FSET is None:
        _DEFAULT_CARDS_FSET = frozenset(_DEFAULT_CARDS)
    return _DEFAULT_CARDS_FSET
