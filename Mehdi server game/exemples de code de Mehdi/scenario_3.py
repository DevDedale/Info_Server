
from game.page import Page
from game.scenario import Scenario
from game.camera import Camera

from game.ui.block import Block
from game.ui.action import ActionButton
from game.ui.content import ContentRow, ContentActionRow
from game.ui.row import RowStaticText, RowDynamicText, RowChecklist, RowPasscode, RowButton
from game.ui.row import RowDoor, RowLedBar, RowImageBlock, RowSlider
from game.ui.row import RowPushButton, RowDialogInput
from game.ui.appbar import AppBarDynamicText
import game.ui.html as html

from test_package.test_module import MyTestClass

import time, math, random

class MDC1(Scenario):
    NAME = "Cauchemar"
    DESCRIPTION = "Scénario de la maison du cauchemar"
    AUTOLOAD = False
 
    THEME_MAIN_COLOR = "#454545"
    THEME_APP_BAR_IMAGE_SRC = "/bar_logo.png"
    THEME_APP_BAR_BACKGROUND_SRC = "/bar.png"
    THEME_NAVIGATION_DRAWER_IMAGE_SRC = "/drawer.png"

    def initialize(self):
        pass

    def get_cameras(self):
        srvip = "10-0-0-89.test.jdam.local.magichanism.com"
        unison_mic_url = "wss://{}/unison-microphone/".format(srvip)
        unison_mon_url = "wss://{}/unison-monitor/".format(srvip)

        def mir_url(name, q=""):
            return "wss://{}/mir/streams/{}{}".format(
                srvip, name, q
                )

        camera_positions = [
            ("left", "à gauche"),
            ("right", "à droite"),
            ("up", "en haut"),
            ("down", "en bas"),
        ]

        def _on_camera_position(pos):
            self.logic.log_debug("camera pos changed {}".format(pos))

        def _on_message(msg):
            self.logic.log_debug("message to players: {}".format(msg))

        cameras = []
        for i,(name,longname,monzone) in enumerate([
            ("webcam2","Salon","zone0"),
            ("webcam2","Webcam","zone1"),
            ("webcam2","Webcam","zone2"),
            ("webcam2","Webcam","zone3"),
            ("webcam2","Webcam","zone4"),
            ]):
            cameras.append(
                Camera(
                    name + str(i), longname + " " + str(i),
                    mir_url(name, "_lq"), 4/3,
                    mir_url(name, ""), 16/9,
                    unison_mon_url, monzone,
                    unison_mic_url, "test",
                    camera_positions, _on_camera_position,
                    "send message to {}".format(name), _on_message,
                )
            )
        return cameras



    def get_app_bar_ui(self):
        def _update_timer(_):
            timestr = time.strftime("%H:%M:%S")
            self.logic.globals.named("TIMER").set(
                html.span_formatter(timestr, size="20px", smallcaps=True)
            )
        self.logic.scheduler.every(.75, _update_timer)

        return [
            AppBarDynamicText(self.logic.globals.named("TIMER"))
        ]

    def get_ui(self):

        GN = self.logic.globals.named

        GN("lo-necro").set(True)
        GN("lo-satan").set(True)
        GN("lo-pro").set(True)

        GN("invoc-locked").set(True)

        GN("PS1").set(2)

        return [

            Page(
                phase = "Administration",
                name = "Configuration",
                ui = [
                    # -- bibliothèque --
                    Block(
                        title = "Configuration du salon",
                        header = [
                        ],
                        content = [
                            ContentRow([
                                RowSlider(GN("A-3"), "ambiance",
                                  vmin=-99, vmax=10, vstep=1, unit="dB",
                                  prepend_icon="mdi-volume-low", append_icon="mdi-volume-high"),
                                RowSlider(GN("A-2"), "bruit foudre",
                                  vmin=-99, vmax=10, vstep=1, unit="dB",
                                  prepend_icon="mdi-volume-low", append_icon="mdi-volume-high"),
                                RowSlider(GN("A-1"), "bruit placard",
                                  vmin=-99, vmax=10, vstep=1, unit="dB",
                                  prepend_icon="mdi-volume-low", append_icon="mdi-volume-high"),
                                RowSlider(GN("A0"), "fuyez...",
                                  vmin=-99, vmax=10, vstep=1, unit="dB",
                                  prepend_icon="mdi-volume-low", append_icon="mdi-volume-high"),
                                RowSlider(GN("A1"), "Ce tombeau...",
                                  vmin=-99, vmax=10, vstep=1, unit="dB",
                                  prepend_icon="mdi-volume-low", append_icon="mdi-volume-high"),
                                RowSlider(GN("A2"), "Plafonnier",
                                  vmin=0, vmax=100, vstep=1, unit="%",
                                  prepend_icon="mdi-lightbulb-off", append_icon="mdi-lightbulb-on"),
                                RowSlider(GN("A3"), "Lampe",
                                  vmin=0, vmax=100, vstep=1, unit="%",
                                  prepend_icon="mdi-lightbulb-off", append_icon="mdi-lightbulb-on"),
                                RowSlider(GN("A4"), "Couloir",
                                  vmin=0, vmax=100, vstep=1, unit="%",
                                  prepend_icon="mdi-lightbulb-off", append_icon="mdi-lightbulb-on"),
                                RowSlider(GN("A5"), "Chevet",
                                  vmin=0, vmax=100, vstep=1, unit="%",
                                  prepend_icon="mdi-lightbulb-off", append_icon="mdi-lightbulb-on"),

                            ]),
                        ],
                        footer = [
                        ],
                    ),

                ]
            ),

            Page(
                phase = "Administration",
                name = "Préparation",
                ui = [
                    # -- bibliothèque --
                    Block(
                        title = "Préparation de la partie",
                        header = [
                        ],
                        content = [
                            ContentRow([
                                RowStaticText("Refermer le placard avec le cadena (code <b>2493</b>)"), RowButton("OK", color="green"),
                            ]),
                            ContentRow([
                                RowStaticText("Éteindre la télévision"), RowButton("OK", color="green"),
                            ]),
                            ContentRow([
                                RowStaticText("Fermer la porte du couloir"), RowButton("OK", color="#555"),
                            ]),

                            ContentRow([
                                RowStaticText("Dès que la salle est prête à recevoir les joueurs appuyez sur <b>EN ATTENTE DES JOUEURS</b>")
                            ]),
                            ContentActionRow([
                                ActionButton("EN ATTENTE DES JOUEURS")
                            ])
                        ],
                        footer = [
                        ],
                    ),

                ]
            ),

            Page(
                phase = "Première partie",
                name = "Salon",
                ui = [
                    # -- bibliothèque --
                    Block(
                        title = "Rangement de la bibliothèque",
                        header = [
                        ],
                        content = [
                            ContentRow([
                                RowStaticText("Les joueurs doivent trouver les 5 livres occultes cachés dans la pièce et les placer sur l'étagère de la bibliothèque (l'ordre n'importe pas)."),
                                RowChecklist("Livres correctement placés",
                                    values=[
                                        (GN("lo-necro"), "Necronomicon"),
                                        (GN("lo-al"), "L'Alchimie pour les nuls"),
                                        (GN("lo-ver"), "Vermis Mysteriis"),
                                        (GN("lo-satan"), "Satan est mon mètre"),
                                        (GN("lo-pro"), "Les prophéties vol.16")

                                    ]),

                            ])
                        ],
                        footer = [
                            ActionButton("FORCER LA RÉUSSITE"),
                        ],
                    ),
                    # -- scéno --
                    Block(
                        title = "Invocation démoniaque",
                        lock = GN("invoc-locked"),
                        lock_text = "Lancer la scénographie pour accéder aux contrôles.",
                        header = [
                            ActionButton("LANCER LA SCÉNOGRAPHIE"),
                        ],
                        content = [
                            ContentRow([
                                RowStaticText("Les lumières du salon s'éteignent et une épaisse fumée se répand."),
                            ]),
                            ContentRow([
                                RowButton("🌩 FOUDRE 🌩",             color="red"),
                                RowButton("CHUTE DU PLACARD",         color="red"),
                                RowButton("🔊 \"CE TOMBEAU SERA...\" 🔊",   color="blue"),
                                RowButton("🔊 \"FUYEZ\" 🔊",                color="blue"),
                            ]),
                        ],
                        footer = [
                            ActionButton("RETOUR À LA NORMALE"),
                        ],
                    ),

                    # -- télévision --
                    Block(
                        title = "Télévision",
                        content = [
                            ContentRow([
                                RowStaticText("La télévision est bloquée par un code parental. Les joueurs doivent l'entrer avec la télécommande pour déverouiller la télévision."),
                                RowPasscode(
                                    "Code parental", 
                                    self.logic.globals.named("PS1"),
                                    expected = "2435"),

                            ]),
                        ],
                        footer = [
                        ],
                    ),


                ]
            ),

            Page(
                phase = "Première partie",
                name = "Cuisine",

            ),

            Page(
                phase = "Seconde partie",
                name = "Couloir",
                ui = [
                    # -- Couloir --
                    Block(
                        title = "Coffre-fort",
                        header = [
                        ],
                        content = [
                            ContentRow([
                                RowStaticText("Un coffre-fort à <b>ouverture manuelle</b> est caché derrière le tableau.<br/>Les joueurs trouvent le code à l'intérieur du carnet de voyage."),
                                RowStaticText("Le code du coffre-fort est {}".format(html.span_formatter("8427", color="white", bold=True))),

                            ]),
                            ContentRow([
                                RowButton("🔊 \"Cherchez mon carnet...\" 🔊",   color="blue"),
                            ]),
                        ],
                        footer = [
                        ],
                    ),
                    # -- Couloir --
                    Block(
                        title = "Accès à la cave",
                        header = [
                        ],
                        content = [
                            ContentRow([
                                RowStaticText("À l'intérieur du coffre-fort les joueurs trouvent un médaillon qui doit être placé sur la porte de la cave pour l'ouvrir."),
                                RowDynamicText("Le médaillon {}.".format(html.span_formatter("n'est pas correctement placé", color="red"))),

                            ]),
                            ContentActionRow([
                                ActionButton("FORCER L'OUVERTURE")
                            ]),
                        ],
                        footer = [
                        ],
                    ),
                    # -- Couloir --
                    Block(
                        title = "Énigme du tableau",
                        header = [
                        ],
                        content = [
                            ContentRow([
                                RowStaticText("Les joueurs trouvent derrière le deuxième tableau un labyrinthe dessiné. La résolution de ce dernier leur permet d'ouvrir la malle contenant le médaillon."),
                                RowImageBlock("Labyrinthe","Version schématique du dessin","https://donjon.bin.sh/fantasy/dungeon/cache/6094136a-56d754fd.png", image_size=(200,"100%")),

                            ]),
                        ],
                        footer = [
                        ],
                    ),

                ]
            ),

            Page(
                phase = "Seconde partie",
                name = "Cave",
                ui = []
            ),

        ]


class MDC3(Scenario):
    NAME = "Cauchemar 2"
    DESCRIPTION = "Scénario alternatif de la maison du cauchemar"
    AUTOLOAD = False
 
    THEME_MAIN_COLOR = "#454545"
    THEME_APP_BAR_IMAGE_SRC = "/favicon-96.webp"
    THEME_NAVIGATION_DRAWER_IMAGE_SRC = ""

    def initialize(self):
        pass

    def get_app_bar_ui(self):
        return []

    def get_ui(self):
        return []

class MDC4(Scenario):
    NAME = "Halloween"
    DESCRIPTION = "Scénario pour la soirée Halloween"
    AUTOLOAD = False
 
    THEME_MAIN_COLOR = "#454545"
    THEME_APP_BAR_IMAGE_SRC = "/favicon-96.webp"
    THEME_NAVIGATION_DRAWER_IMAGE_SRC = ""

    def initialize(self):
        pass

    def get_app_bar_ui(self):
        return []

    def get_ui(self):
        return []


