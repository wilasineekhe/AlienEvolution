"""
main.py
============================================================
Entry point.  Run this file to start the game:

    python main.py          (with venv activated)
    python -m main          (also works)

Game state machine:
    "menu"      -> draw_menu()     Press ENTER
    "playing"   -> Game.update()   ESC -> menu
    "game_over" -> draw_game_over() R -> restart  M -> menu
    "victory"   -> draw_victory()   R -> restart  M -> menu
============================================================
"""

import sys
import pygame

# Initialise pygame before any other imports that use it
pygame.init()
pygame.mixer.init()

from src.constants import SCREEN_W, SCREEN_H, FPS, TITLE, load_fonts
from src.assets    import load_assets, play_sfx
from src.game      import Game
from src.screens   import draw_menu, draw_game_over, draw_victory


def main():
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(TITLE)
    clock  = pygame.time.Clock()

    fonts  = load_fonts()
    assets = load_assets()

    state  = "menu"
    game   = Game(assets, fonts)
    tick   = 0          # global frame counter for menu animations

    running = True
    while running:
        tick += 1
        clock.tick(FPS)

        # ── Event handling ────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if state == "menu":
                    if event.key == pygame.K_RETURN:
                        game  = Game(assets, fonts)
                        state = "playing"

                elif state == "playing":
                    if event.key == pygame.K_ESCAPE:
                        # SOUND: MUSIC -- stop music when going to menu
                        # pygame.mixer.music.stop()
                        state = "menu"

                elif state in ("game_over", "victory"):
                    if event.key == pygame.K_r:
                        game  = Game(assets, fonts)
                        state = "playing"
                    if event.key == pygame.K_m:
                        state = "menu"

        # ── State rendering ───────────────────────────────
        if state == "menu":
            draw_menu(screen, fonts, assets, tick)

        elif state == "playing":
            game.update()

            if not game.player.is_alive:
                game.freeze_timer()          # หยุดเวลา ณ จุดที่ตาย
                # SOUND: GAMEOVER
                play_sfx(assets.get("sfx_gameover"))
                # pygame.mixer.music.stop()
                state = "game_over"

            elif game.player.escaped:
                game.freeze_timer()          # หยุดเวลา ณ จุดที่หนีสำเร็จ
                # victory SFX already fired inside game.update()
                # pygame.mixer.music.stop()
                state = "victory"

            else:
                game.draw(screen)

        elif state == "game_over":
            draw_game_over(screen, fonts, assets,
                           game.player, game.elapsed_seconds())

        elif state == "victory":
            draw_victory(screen, fonts, assets,
                         game.player, game.elapsed_seconds(), tick)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
