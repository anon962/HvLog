import re

def _grp(name, regex):
    return rf"(?P<{name}>{regex})"

_num=    lambda name: _grp(name, r'\d+')
_float=  lambda name: _grp(name, r'\d+(?:\.\d*)?')
_resist= rf"(?: \((?P<resist>\d+)% resisted\))?"
_words=  lambda name: _grp(name, r'[\w\s-]+')
_enemy_spell= rf"{_words('monster')} (?P<spell_type>casts|uses) {_words('skill')}"
_mult_type= lambda *args: _grp('multiplier_type', '|'.join(args))

# @todo: melee
# regex should exactly match each line
PATTERNS= dict(
    # actions
    riddle_success= rf"The RiddleMaster is pleased with your answer, and grants you his blessings\.",
    riddle_fail= rf"You failed to correctly answer the RiddleMaster within the time limit. You lose {_num('value')} Stamina\.",

    player_basic= rf"{_words('name')} {_mult_type('hits', 'crits')} (?!you){_words('monster')} for {_num('value')} {_words('damage_type')} damage\.",
    player_miss= rf"{_words('monster')} {_mult_type('parries')} your attack.",

    player_item= rf"You use {_words('name')}\.",
    player_skill= rf"You cast {_words('name')}\.",

    player_dodge= rf"You {_mult_type('evade', 'parry')} the attack from {_words('monster')}\.",
    enemy_basic= rf"{_words('monster')} {_mult_type('hits', 'crits')} you for {_num('value')} {_words('damage_type')} damage\.",

    enemy_skill_absorb= rf"{_enemy_spell}, but is {_mult_type('absorb')}ed\. You gain {_words('mana')}",
    enemy_skill_miss= rf"{_enemy_spell}\. You {_mult_type('evade', 'parry')} the attack\.",
    enemy_skill_success= rf"{_enemy_spell}, and {_mult_type('hits','crits')} you for {_num('value')} {_words('damage_type')} damage{_resist}\.?",


    # effects
    player_buff= rf"You gain the effect {_words('name')}\.",
    player_skill_damage= rf"{_words('name')} {_mult_type('hits', 'blasts')} {_words('monster')} for {_num('value')} {_words('damage_type')} damage{_resist}",
    riddle_restore= rf"Time Bonus: recovered {_num('hp')} HP and {_num('mp')} MP\.",

    effect_restore= rf"{_words('name')} restores {_num('value')} points of (?P<type>\w+)\.",
    item_restore= rf"Recovered {_num('value')} points of (?P<type>\w+)\.",
    cure_restore= rf"You are healed for {_num('value')} Health Points\.",

    spirit_shield= rf"Your spirit shield absorbs {_num('damage')} points of damage from the attack into {_num('spirit_damage')} points of spirit damage\.",
    spark_trigger= rf"Your Spark of Life restores you from the brink of defeat\.",

    dispel= rf"The effect {_words('name')} was dispelled\.",
    cooldown= rf"Cooldown expired for {_words('name')}",
    buff_expire= rf"The effect {_words('name')}  has expired\.",

    enemy_resist= rf"{_words('monster')} resists your spell\.",
    enemy_debuff= rf"{_words('monster')} gains the effect {_words('name')}\.",
    debuff_expire= rf"The effect {_words('name')} on {_words('monster')} has expired.",


    # info
    round_end= rf"You are Victorious!",
    round_start= rf"Initializing " + _grp('battle_type', r'[\w\s\d#]+') + rf" \(Round {_num('current')} / {_num('max')}\) \.\.\.",

    spawn= rf"Spawned Monster (?P<letter>[A-Z]): MID={_num('mid')} \({_words('monster')}\) LV={_num('level')} HP={_num('hp')}",
    death= rf"{_words('monster')} has been defeated\.",

    gem= rf"{_words('monster')} drops a (?P<type>\w+) Gem powerup!",
    gf_credits= rf"You gain ({_num('value')}) Credits!",
    drop= rf"{_words('monster')} dropped \[(?P<item>.*)\]",
    prof= rf"You gain {_float('value')} points of {_words('type')} proficiency\.",
    exp= rf"You gain {_num('value')} EXP!",
    auto_salvage= rf"A traveling salesmoogle salvages it into {_num('value')}x \[(?P<item>[\w\s-]+)\]",
    auto_sell= rf"A traveling salesmoogle gives you \[{_num('value')} Credits\] for it\.",

    clear_bonus= rf"Battle Clear Bonus! \[{_words('item')}\]",
    token_bonus= rf"Arena Token Bonus! \[{_words('item')}\]",
    event= rf"You found a \[{_words('item')}\]",

    mb_usage= rf"Used: (.*)"
)
PATTERNS= {x : re.compile(y) for x,y in PATTERNS.items()}

# @todo: assert all patterns used
# @todo: Unlocked innate potential: Juggernaut Level 4
# @todo: The equipment's potential has increased by 1560 points!
# @todo: Yggdrasil casts Healing Roots, healing Verdandi for 156 points of health.
# @todo: A shimmering light is pulsating from Yggdrasil...
# @todo: Your spell is absorbed.
# @todo: You have escaped from the battle.
# @todo: Spirit Stance Engaged
# @todo: You obtained 5x [Soul Fragments] --- Iseaki
# @todo: Your Spark of Life fails due to insufficient Spirit.
