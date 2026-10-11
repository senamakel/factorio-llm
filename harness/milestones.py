"""Pure scoring for brain episodes: the ladder of milestones and the composite score.

Rates come from the *automation window*: after the brain's time is up, the
harness stops the actor (no walking, mining or handcrafting) and lets the
world run for a fixed number of game minutes. Only machines produce during
that window, so every per-minute rate here is factory output, not handcraft.
"""

RED, GREEN = 'automation-science-pack', 'logistic-science-pack'
CAP = 100

LADDER = (
    ('G1', 'Automation researched'),
    ('G2', 'An assembling machine has crafted something'),
    ('G3', 'Red packs produced by machines in the automation window'),
    ('G4', 'Ore mined and iron plates smelted by machines in the automation window'),
    ('G5', '>= 10 red packs/min sustained'),
    ('G6', '>= 30 red packs/min sustained'),
    ('G7', '>= 100 red packs/min sustained'),
    ('G8', 'Logistic science pack researched and an electric mining drill built'),
    ('G9', 'Green packs produced by machines in the automation window'),
    ('G10', '>= 10 green packs/min sustained'),
    ('G11', '>= 30 green packs/min sustained and Automation 2 researched'),
    ('G12', '>= 100 red and >= 100 green packs/min sustained'),
)


def window_rates(start, end, minutes):
    """Return items per minute between two production samples ``{item: produced}``."""
    if minutes <= 0:
        raise ValueError('window must be positive')
    return {item: max(0, end.get(item, 0) - start.get(item, 0)) / minutes for item in end}


def reached(world, rates):
    """Evaluate every ladder milestone from read-back world facts and window rates.

    ``world`` holds ``researched`` (set of technology names), ``entity_counts``
    ({name: n}) and ``assembler_products`` (total products_finished by
    assembling machines). ``rates`` maps item name to per-minute production
    during the automation window.
    """
    red, green = rates.get(RED, 0), rates.get(GREEN, 0)
    researched, counts = set(world['researched']), world['entity_counts']
    return {
        'G1': 'automation' in researched,
        'G2': world['assembler_products'] > 0,
        'G3': red > 0,
        'G4': rates.get('iron-ore', 0) > 0 and rates.get('iron-plate', 0) > 0,
        'G5': red >= 10,
        'G6': red >= 30,
        'G7': red >= 100,
        'G8': 'logistic-science-pack' in researched and counts.get('electric-mining-drill', 0) > 0,
        'G9': green > 0,
        'G10': green >= 10,
        'G11': green >= 30 and 'automation-2' in researched,
        'G12': red >= 100 and green >= 100,
    }


def score(rates, milestones):
    """Composite: capped red/min + capped green/min + 5 per milestone reached (max 260)."""
    return min(rates.get(RED, 0), CAP) + min(rates.get(GREEN, 0), CAP) + 5 * sum(milestones.values())


def next_goal(milestones):
    """Return the first unreached ladder step as ``(id, description)``, or None when done."""
    return next(((key, text) for key, text in LADDER if not milestones.get(key)), None)
