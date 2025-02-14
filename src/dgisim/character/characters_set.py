from typing import FrozenSet, Type

from .character import *

__all__ = [
    "default_characters",
]

_DEFAULT_CHARACTERS: list[type[Character]] = [
    Albedo,
    AratakiItto,
    Bennett,
    Chongyun,
    Collei,
    Dehya,
    Diona,
    ElectroHypostasis,
    Eula,
    FatuiCryoCicinMage,
    FatuiPyroAgent,
    Fischl,
    Ganyu,
    HuTao,
    JadeplumeTerrorshroom,
    Jean,
    KaedeharaKazuha,
    Kaeya,
    KamisatoAyaka,
    Keqing,
    Klee,
    KujouSara,
    Layla,
    Lisa,
    Lyney,
    MaguuKenki,
    Mona,
    Nahida,
    Ningguang,
    Noelle,
    Qiqi,
    RaidenShogun,
    RhodeiaOfLoch,
    SangonomiyaKokomi,
    Shenhe,
    StonehideLawachurl,
    Tartaglia,
    Tighnari,
    Venti,
    Wanderer,
    Xingqiu,
    YaeMiko,
    Yaoyao,
    Yelan,
    Yoimiya,
]

_DEFAULT_CHARACTER_FSET = None


def default_characters() -> frozenset[type[Character]]:
    global _DEFAULT_CHARACTER_FSET
    if _DEFAULT_CHARACTER_FSET is None:
        _DEFAULT_CHARACTER_FSET = frozenset(_DEFAULT_CHARACTERS)
    return _DEFAULT_CHARACTER_FSET
