"""Easy sandbox defaults for new worlds, independent of the enabled expansion mods."""

RESOURCES = ('iron-ore', 'copper-ore', 'coal', 'stone', 'uranium-ore', 'crude-oil')


def easy_map_settings():
    """Return a fresh no-enemy map configuration with 600% ore size/richness."""
    return {'peaceful_mode':True, 'no_enemies_mode':True, 'starting_area':6,
            'autoplace_controls':{
                **{name:{'frequency':3,'size':6,'richness':6} for name in RESOURCES},
                'enemy-base':{'frequency':0,'size':0,'richness':0}}}
