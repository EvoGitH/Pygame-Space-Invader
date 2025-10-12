import pygame
from modules.assets import Assets
from modules.upgrades import Upgrades
from modules.button import Button


class Shop:
    """Player Shop
    functions defined are
    Shop background, and
    Shop's buying function
    
    Update the key_map to add
    new upgrades to shop."""

    def __init__(self, player, info):
        self.player = player
        self.info = info

        self.active = False
        self.key_map = {
            pygame.K_1: "Speed",
            pygame.K_2: "Triple Shot",
            pygame.K_3: "Side Cannon"
        }
        
        self.buttons = []
        y_offset = 200
        for key, upgrade_name in self.key_map.items():
                upgrade_info = Upgrades.upgrades[upgrade_name]
                button_text = f"[{pygame.key.name(key).upper()}] {upgrade_name} ({upgrade_info['cost']}, Max: {upgrade_info['max_purchases']})"
                self.buttons.append(
                    Button(
                        x=info.screenX // 2 - 150,
                        y=y_offset,
                        width=400,
                        height=71,
                        text=button_text,
                        color=(0,128,255),
                        hover_color=(0,200,255),
                        action=lambda n=upgrade_name: self.buy_upgrade_by_name(n)
                    )
                )
                y_offset += 90

        self.back_button = Button(
            x=20,
            y=40,
            width=100,
            height=50,
            text="BACK",
            color=(255,0,0),
            hover_color=(255,100,100),
            action=self.close_shop 
        )

    def buy_upgrade_by_name(self, upgrade_name):
        upgrade = Upgrades.upgrades[upgrade_name]

        if upgrade["times_purchased"] >= upgrade["max_purchases"]:
            self.info.show_message(f"{upgrade_name} already maxed out!", duration=1000)
            return

        if self.player.credits >= upgrade["cost"]:
            self.player.credits -= upgrade["cost"]

            upgrade["effect"](self.player)
            upgrade["times_purchased"] += 1

            remaining = upgrade["max_purchases"] - upgrade["times_purchased"]
            if remaining > 0:
                self.info.show_message(f"{upgrade_name} purchased! ({remaining} remaining). Credits: {self.player.credits}", duration=1000)
            else:
                self.info.show_message(f"{upgrade_name} fully upgraded!", duration=1000)
        else:
            self.info.show_message("Not enough credits!", duration=1000)
        
    def buy_upgrade_by_key(self, key):
        if key in self.key_map:
            upgrade_name = self.key_map[key]
            self.buy_upgrade_by_name(upgrade_name)
    
    def draw(self, screen):
        if not self.active:
            return
        screen.blit(Assets.background_image, (0, 0))

        for button in self.buttons:
            button.draw(screen)

        self.back_button.draw(screen)
        font = pygame.font.Font(None, 40)
        money_text = font.render(f"CREDITS: {self.player.credits}", True, (255, 255, 255))
        screen.blit(money_text, (15, 120))
        info_text = font.render("ESC to Resume", True, (255, 255, 255))
        screen.blit(info_text, (15, 500))

    def handle_event(self, event):
        if not self.active:
            return
        for button in self.buttons:
            button.handle_event(event)
            
        self.back_button.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key not in self.key_map:
                self.buy_upgrade_by_key(event.key)
            if event.key == pygame.K_ESCAPE:
                self.active = False

    def close_shop(self):
        self.active = False