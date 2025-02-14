# Change Log

## 0.6.0 (To be released)

### Added

- Enabled flipped encoding of a game. (Make P2 P1 and vice versa)
- Enabled ordered flat encoding for dice and cards

---

- New Characters:
  - Chongyun
  - Diona
  - Fatui Cryo Cicin Mage
  - Layla
  - Lisa
  - Lyney
  - Stonehide Lawachurl
  - Yaoyao
  - Yelan
- New Cards:
  - Equipment Cards:
    - Talent Cards:
      - Beneficent
      - Cicin's Cold Glare
      - Conclusive Ovation
      - Light's Remit
      - Pulsating Witch
      - Shaken, Not Purred
      - Steady Breathing
      - Stonehide Reforged
      - Turn Control
    - Artifact Cardso
      - Crown of Watatsumi
      - Echoes of an Offering
      - Emblem of Severed Fate
      - Exile's Circlet
      - Ocean-Hued Clam
      - Ornate Kabuto
  - Support Cards:
    - Companion Cards:
      - Jeht
      - Timmie
    - Item Cards:
      - Memento Lens
      - Red Feather Fan
      - Seed Dispensary
    - Location Cards:
      - Dawn Winery
      - Gandharva Ville
      - Golden House
      - Jade Chamber
      - Opera Epiclese
      - Stormterror's Lair
      - Weeping Willow of the Lake
  - Event Cards:
    - Food Cards:
      - Fish and Chips
      - Sashimi Platter
    - Other Cards:
      - Sunyata Flower

### Updated

- Applied version 4.4's balance patch (forgot to mention in 0.5.0).
- Applied version 4.5's balance patch
- Applied version 4.6's balance patch
- Applied version 4.7's balance patch
- Applied version 4.8's balance patch
- Improved encoding for enums in the game such that encoded state always use
  different ID for different enums of different type.
- Renamed `EncodingPlan.code_for` to `EncodingPlan.encode_item`.

### Fixed

- Faulty description of size of encoded player state in documentation.
- Faulty execution order of damage, swap, healing signals
- Faulty deduction order or elemental dice cost

## 0.5.0 (31 Jan 2024)

### Added

- New Characters:
  - Raiden Shogun
- New Cards:
  - Equipment Cards:
    - Artifact Cards:
      - Archaic Petra
      - Blizzard Strayer
      - Broken Rimes Echo
      - Crimson Witch of Flames
      - Deepwood Memories
      - Heart of Depth
      - Laurel Coronet
      - Mask of Solitude Basalt
      - Thunder Summoner's Crown
      - Thundering Fury
      - Viridescent Venerer
      - Viridescent Venerer's Diadem
      - Wine-Stained Tricorne
      - Witchs Scorching Hat
    - Talent Cards:
      - Wishes Unnumbered
  - Event Cards:
    - Other Cards:
      - Strategize (added in 0.4.0 but missed in CHANGELOG)

### Updated

- Loosen version requirement for dependency "typing-extensions"

### Fixed

- "Blessing of the Divine Relic's Installation" and "Master of Weaponry"
  don't trigger on enter effects

## 0.4.0 (15 Jan 2024)

### Added

- New Characters:
  - Eula
  - Kamisato Ayaka
  - Kujou Sara
  - Tartaglia
  - Wanderer
- New Cards:
  - Equipment Cards:
    - Talent Cards:
      - Abyssal Mayhem Hydrospout
      - Gales of Reverie
      - Kanten Senmyou Blessing
      - Sin of Pride
      - Wellspring of War-Lust
    - Weapon Cards:
      - Bow:
        - Elegy of the End
      - Polearm:
        - Engulfing Lightning
        - Moonpiercer
      - Sword:
        - Favonius Sword
    - Artifact Cards:
      - Flowing Rings
      - Gilded Dreams
      - Heart of Khvarena's Brilliance
      - Shadow of the Sand King
      - Vourukasha's Glow
  - Support Cards:
    - Chef Mao
    - Dunyarzad
    - Liu Su
    - Mamere
    - Master Zhang
    - Rana
    - Setaria
    - Timaeus
    - Treasure-Seeking Seelie
    - Wagner
    - Yayoi Nanatsuki
  - Event Cards:
    - Arcane Legend Cards:
      - Ancient Courtyard
      - Covenant of Rock
      - In Every House a Stove
      - Joyous Celebration
      - Passing of Judgment
      - Toss-Up
    - Food Cards:
      - Adeptus' Temptation
      - Butter Crab
    - Other Cards:
      - Abyssal Summons
      - Blessing of the Divine Relic's Installation
      - Guardian's Oath
      - Heavy Strike
      - Lyresong
      - Master of Weaponry
      - Nature and Wisdom
      - Stone and Contracts
      - The Boar Princess
      - Thunder and Eternity

### Updated

- Adjusted encoding of PlayerState to support new card in game version 4.3
- Version 4.3 balance patch applied
- Improved swap signal handling
- Refactored some get methods in GameState, PlayerState and Character into property methods

### Removed

- equipment statuses methods in PlayerState

## 0.3.4 (3 Dec 2023)

### Added

- Subclasses of `Deck` now supports conversion to and from json by calling
  `.to_json()` and `.from_json()`.
- Enables seeding when stepping `GameState`
- Implements customizable encoding for any `GameState`
- Smart dice selection that takes characters into account
- Implements `LinearEnv`, a gym-like environment for RL
- Implements `PlayerAction` encoding and decoding
- Implements `MutableDeck`, `FrozenDeck` encoding and decoding
- New Cards:
  - Event Card:
    - Fresh Wind of Freedom
    - When the Crane Returned

### Updated

- All the implemented cards and characters are now up-to-date with game version
  4.2.
- Perspective view of `GameState` now hides the dice of the opponent.
  (The only things left to hide are some certain statuses and effects)

### Fixed

- AbstractDice.cost_less_elem() has faulty behaviour when only ANY can be reduced.
- Hand card limit set in game mode was not enforced throughout the game.

## 0.3.3 (5 Nov 2023)

### Added

`dgisim` includes enum `ActionType` for action choosing.

- New Characters:
  - Dehya
  - Hu Tao
- New Cards:
  - Equipment Card:
    - Talent Equipment Card:
      - Sanguine Rouge
      - Stalwart and True

## 0.3.2 (24 Oct 2023)

Removes preceding `v` in version name to be like `0.3.2`.

### Added

- New Characters:
  - Albedo
  - Collei
  - Fatui Pyro Agent
  - Fischl
  - Ganyu
  - Jadeplume Terrorshroom
  - Jean
  - Maguu Kenki
  - Ningguang
  - Qiqi
  - Sangonomiya Kokomi
  - Yoimiya
- New Cards:
  - Equipment Card:
    - Talent Equipment Card:
      - Descent of Divinity
      - Floral Sidewinder
      - Lands of Dandelion
      - Naganohara Meteor Swarm
      - Paid in Full
      - Proliferating Spores
      - Rite of Resurrection
      - Stellar Predator
      - Strategic Reserve
      - Tamakushi Casket
      - Transcendent Automaton
      - Undivided Heart
    - Weapon Card:
      - A Thousand Floating Dreams
      - Amos' Bow
      - Aquila Favonia
      - Fruit of Fulfillment
      - King's Squire
      - Lithic Spear
      - The Bell
      - Vortex Vanquisher
      - Wolf's Gravestone
    - Artifact Card:
      - General's Ancient Helm
      - Instructor's Cap
      - Tenacity of the Millelith
  - Support Card:
    - Companion Card:
      - Chang the Ninth
      - Liben
      - Paimon
    - Item Card:
      - NRE
      - Parametric Transformer
    - Location Card:
      - Liyue Harbor Wharf
      - Sumeru City
      - Tenshukaku
  - Event Card:
    - Send Off
    - Tandoori Roast Chicken
    - The Bestest Travel Companion!
    - Where Is the Unseen Razor?

## v0.3.1 (28 Aug 2023)

### Added

- New Characters:
  - Bennett
  - Nahida
  - Noelle
  - Shenhe
  - Venti
  - Yae Miko
- New Cards:
  - Equipment Card:
    - Talent Equipment Card:
      - Embrace of Winds
      - Grand Expectation
      - I Got Your Back
      - Mystical Abandon
      - The Seed of Stored Knowledge
      - The Shrine's Sacred Shade
    - Weapon Card:
      - Sacrificial Bow
      - Sacrificial Fragments
      - Sacrificial Greatsword
      - Sacrificial Sword
  - Event Card:
    - Elemental Resonance: Enduring Rock
    - Elemental Resonance: Fervent Flames
    - Elemental Resonance: High Voltage
    - Elemental Resonance: Impetuous Winds
    - Elemental Resonance: Shattering Ice
    - Elemental Resonance: Soothing Water
    - Elemental Resonance: Sprawling Greenery
    - Elemental Resonance: Woven Flames
    - Elemental Resonance: Woven Ice
    - Elemental Resonance: Woven Stone
    - Elemental Resonance: Woven Thunder
    - Elemental Resonance: Woven Waters
    - Elemental Resonance: Woven Weeds
    - Elemental Resonance: Woven Winds
    - Wind and Freedom

## v0.3.dev0 (6 Aug 2023)

### Added

- **Deck** related classes with card validity checking
- New Characters:
  - Electro Hypostasis
  - Mona
  - Xingqiu
- New Cards:
  - Talent Equipment Card:
    - Prophecy of Submersion
    - The Scent Remained
  - Artifact Card:
    - Gambler's Earrings
  - Location Card:
    - Knights of Favonius Library
    - Vanarana
  - Event Card:
    - I Haven't Lost Yet!
    - Food Card:
      - Teyvat Fried Egg
    - Talent Card:
      - Absorbing Prism

## v0.2.dev3 (27 Jul 2023)

### Added

At least one character of each element is now implemented

- New Characters:
  - Arataki Itto
  - Kaedehara Kazuha
  - Klee
  - Tighnari
- New Cards:
  - Charcter Talenet Card:
    - Arataki Ichiban
    - Keen Sight
    - Poetics of Fuubutsu
    - Pounding Surprise
  - Weapon Card:
    - Magic Guide
    - Raven Bow
    - Traveler's Handy Sword
    - White Iron Greatsword
    - White Tassel
  - Event Card:
    - Calxs Arts
    - Quick Knit

### Updated

- minor API change

## v0.2.dev2 (9 Jul 2023)

### Updated

- minor API change

## v0.2.dev1 (9 Jul 2023)

### Added

- methods to quick-create GameState / PlayerState / Characters
- includes some container classes in root dgisim
- unifies PS1 format

## v0.2.dev0 (9 Jul 2023)

### Added

- Adds link to documentation

### Updated

- Refines API
- CLI has full control of the player

## v0.1.dev0 (3 Jul 2023)

### Added

- Gives user the access to entire repo's src modules
