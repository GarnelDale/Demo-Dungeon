import arcade
from arcade.color import BLUE_YONDER, GRAY, NAVY_BLUE, WHITE
from arcade.text import draw_text

# Constants for the game window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Demo Dungeon"

# Constants for Sprites
CHARACTER_SCALING = 1
TILE_SCALING = 0.5

# Movement constants
MOVEMENT_SPEED = 4
ENEMY_MOVEMENT_SPEED = 2

# Viewport constants for scrolling
LEFT_VIEWPOINT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = 250
BOTTOM_VIEWPORT_MARGIN = 100
TOP_VIEWPORT_MARGIN = 100


class Character(arcade.Sprite):
    """ Class for friend and foe sprites that feature animations and
        individual sprite sheets"""
    def __init__(self, texture_source):
        super().__init__()
        # Score for victory condition
        self.score = 0

        # Passed in texture for individual object instances
        self.texture = arcade.load_texture(texture_source)

        # Animation loading and controls would go here
        
        # basic hitbox square based on assumption that the models are only 32x32
        # pixels
        self.set_hit_box([[-16, -16], [16, -16], [16, 16], [-16, 16]])

    # Getter/setter for score
    def change_score(self, value):
        self.score += value
    
    def enemy_walk(self):
        # Goblin is on the right side of the square
        if self.center_x >= 1500:
             # Walk up
            if self.center_y < 1180:
                self.angle = 0
                self.change_x = 0
                self.change_y = ENEMY_MOVEMENT_SPEED
             # Walk left
            elif self.center_y >= 1180:
                self.angle = 90
                self.change_x = -MOVEMENT_SPEED
                self.change_y = 0
        # Goblin is on the left side of the square
        elif self.center_x <= 1125:
            # Walk down
            if self.center_y >= 1180:
                self.angle = 180
                self.change_x = 0
                self.change_y = -MOVEMENT_SPEED
            # Walk right
            elif self.center_y <= 830:
                self.angle = 270
                self.change_x = MOVEMENT_SPEED
                self.change_y = 0
        
        self.center_x += self.change_x
        self.center_y += self.change_y
    


class GameView(arcade.View):
    """
    Main application class.
    """
    # Constructor for the game window and assets
    def __init__(self):
        super().__init__()
        
        # Lists for sprite management
        self.player_list = None
        self.gem_list = None
        self.foe_list = None
        self.wall_list = None
        self.danger_list = None

        # Player sprite
        self.player_sprite = None
        self.enemy_sprite = None
        self.escape = None

        # Initialize our movement engine
        self.physics_engine = None

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Initialize our background
        self.background = None

        # Load background music and sound effects
        self.introduction = None
        self.bgm = None

        

        

    def setup(self):
        """ Set up the game here. Call this function to restart the game"""
        # Create the sprite lists
        self.player_list = arcade.SpriteList()
        self.gem_list = arcade.SpriteList(use_spatial_hash=True)
        self.foe_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.danger_list = arcade.SpriteList(use_spatial_hash=True)

        # Draw player sprite at specific coordinates  
        self.player_sprite = Character('resources/warrior.png')
        self.player_sprite.center_x = 800
        self.player_sprite.center_y = 100
        self.player_list.append(self.player_sprite)

        # Prep and draw enemy sprite at specific location
        self.enemy_sprite = Character('resources/goblin.png')
        self.enemy_sprite.center_x = 1500
        self.enemy_sprite.center_y = 830
        self.foe_list.append(self.enemy_sprite)

        #  Escape portal sprite
        self.escape = arcade.SpriteCircle(16,BLUE_YONDER)
        self.escape.center_x = 1500
        self.escape.center_y = 636

        # Load in the background art
        self.background = arcade.load_texture("resources/floorTemp.png")

        # Setting view-port to default
        self.view_bottom = 0
        self.view_left = 0

        # Load music and sfx for game
        self.intro = arcade.load_sound("resources/intro.wav")
        self.music = arcade.load_sound("resources/finalLoop.wav")
        self.gem_collect = arcade.load_sound("resources/coin2.wav")
        self.death = arcade.load_sound("resources/hit2.wav")

        # Start playing BGM
        self.introduction = arcade.play_sound(self.intro, .5, 0, False)


        # Name of map file to load
        map_name = "resources/Demo Dungeon.tmx"
        # Name of the layer in the file that has our walls
        walls_layer_name = 'Dungeon'
        # Name of the layer that has environmental hazards
        danger_layer_name = 'Dangers'
        # Name of the layer that has pick ups
        gem_layer_name = 'Gems'

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)

        # -- Dungeon structure
        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=walls_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)

        # -- Environmental hazards
        self.danger_list = arcade.tilemap.process_layer(map_object=my_map, 
                                                        layer_name=danger_layer_name, 
                                                        scaling=TILE_SCALING, 
                                                        use_spatial_hash=True)


        # -- Gem locations
        self.gem_list = arcade.tilemap.process_layer(map_object=my_map, 
                                                     layer_name=gem_layer_name, 
                                                     scaling=TILE_SCALING, 
                                                     use_spatial_hash=True)

        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(GRAY)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, 
                                                         self.wall_list)

    def on_draw(self):
        """ Render the screen. """
        # Clear the screen to background color
        arcade.start_render()
        
        arcade.draw_lrwh_rectangle_textured(self.view_left, self.view_bottom, 
                                            SCREEN_WIDTH, SCREEN_HEIGHT, 
                                            self.background)

        # Draw the sprites from the lists
        self.wall_list.draw()
        self.danger_list.draw()
        self.gem_list.draw()
        self.escape.draw()
        self.player_list.draw()
        self.foe_list.draw()
       
        # Score tally in the top left corner of the screen
        arcade.draw_text(f"SCORE: {self.player_sprite.score}", 
                         self.view_left, self.view_bottom + SCREEN_HEIGHT - 15, 
                         WHITE)

    def on_key_press(self, key, modifiers):
        """Called when a key is pressed"""

        # Adds movement speed to the x or y axis and direction for player model
        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.angle = 0
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.angle = 180
            self.player_sprite.change_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.angle = 90
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.angle = 270
            self.player_sprite.change_x = MOVEMENT_SPEED
    
    def on_key_release(self, key, modifiers):
        """Called when a key is released"""

        # Clear movement speed when key is released
        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0        

    def update(self, delta_time):
        """ Movement and game logic """

        # Move the player with the physics engine
        self.physics_engine.update()

        # Run main BGM loop if intro is finished
        position = self.intro.get_stream_position(self.introduction)
        if position == 0 and self.bgm == None:
            self.bgm = arcade.play_sound(self.music, .5, 0, True)

        # Make goblin patrol
        self.enemy_sprite.enemy_walk()

        # See if we hit any hazards or enemies
        danger_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                               self.danger_list)
        danger_hit_list += arcade.check_for_collision_with_list(self.player_sprite, 
                                                                self.foe_list)
        
        if danger_hit_list:
            # "Kill" player, play death sound, and move to the game over screen
            self.player_sprite.kill()
            arcade.play_sound(self.death)

            # End music
            if self.intro.is_playing(self.introduction):
                arcade.stop_sound(self.introduction)
            else:
                arcade.stop_sound(self.bgm)

            game_view = EndingView(1)
            self.window.show_view(game_view)

        # See if we have collected any gems
        gem_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                            self.gem_list)

        for gem in gem_hit_list:
            gem.remove_from_sprite_lists()
            self.player_sprite.change_score(1)
            arcade.play_sound(self.gem_collect)

        # --- Manage Scrolling ---

        # Track if we need to change the viewport
        changed = False

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPOINT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True
        
        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True
        
        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True
        
        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True
        
        if changed:
            # Only scroll full integers to avoid mismanagement of pixels
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)

        # Game finish condition
        self.exit_access = arcade.check_for_collision(self.player_sprite, 
                                                      self.escape)
        if self.player_sprite.score == 5 and self.exit_access:
            # End music
            if self.intro.is_playing(self.introduction):
                arcade.stop_sound(self.introduction)
            else:
                arcade.stop_sound(self.bgm)

            # Move to victory screen
            game_view = EndingView(2)
            self.window.show_view(game_view)

    

class TitleView(arcade.View):
    """ Class for a title screen and controls to start game """
    def on_show(self):
        arcade.set_background_color(NAVY_BLUE)
        arcade.set_viewport(0,SCREEN_WIDTH-1,0,SCREEN_HEIGHT-1)

    def on_draw(self):
        """ Draw title screen """
        arcade.start_render()
        arcade.draw_text("Demo Dungeon", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Press Enter to begin", SCREEN_WIDTH / 2, 
                         SCREEN_HEIGHT / 2-75, arcade.color.WHITE, font_size=20, 
                         anchor_x="center")

    def on_key_press(self, key, modifiers):
        """ Progress if Enter is pressed """ 
        if key == arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)

class EndingView(arcade.View):
    """ Class for ending screens """
    def __init__(self, end):
        super().__init__()
        self.close = end
        arcade.set_background_color(NAVY_BLUE)
        arcade.set_viewport(0,SCREEN_WIDTH-1,0,SCREEN_HEIGHT-1)

    def on_draw(self):
        """ Draw win or lose screens"""
        arcade.start_render()
        arcade.set_viewport(0,SCREEN_WIDTH-1,0,SCREEN_HEIGHT-1)

        if self.close == 1:
            arcade.draw_text("GAME OVER", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         arcade.color.RED, font_size=50, anchor_x="center")
            arcade.draw_text("Press Enter to play again", SCREEN_WIDTH / 2,
                             SCREEN_HEIGHT / 2-75, arcade.color.RED,
                             font_size=20, anchor_x="center")
        else:
            arcade.draw_text("YOU ESCAPED THE DUNGEON", SCREEN_WIDTH / 2, 
                             SCREEN_HEIGHT / 2, arcade.color.GOLD, 
                             font_size=50, anchor_x="center")
            arcade.draw_text("Press Enter to play again", SCREEN_WIDTH / 2,
                             SCREEN_HEIGHT / 2-75, arcade.color.GOLD,
                             font_size=20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)


def main():
    """ Main method """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = TitleView()
    window.show_view(start_view)
    arcade.run()

if __name__ == "__main__":
    main()