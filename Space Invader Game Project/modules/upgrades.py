class Upgrades:
    """ Will contain the player
    shop inventory, and be updatable
    as needed. 

    Visit "class Shop" to update key_map, buttons, etc.

    Example: *setattr(class/"object", variable/"attribute name", effect/"value")*
    """

    upgrades = {
    "Speed": {
        "cost": 500,
        "effect": lambda player: setattr(player, "speed", player.speed + 1),
        "times_purchased": 0,
        "max_purchases": 5    
    },
    "Triple Shot": {
        "cost": 800,
        "effect": lambda player: setattr(player, "triple_shot_unlocked", True),
        "times_purchased": 0,
        "max_purchases": 1
    },
    "Side Cannon": {
        "cost": 1000,
        "effect": lambda player: setattr(player, "side_cannon_count", min(player.side_cannon_count + 1, player.side_cannon_max)),
        "times_purchased": 0,
        "max_purchases": 2
    },
}