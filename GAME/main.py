import os
import sys
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from random import  randint
import time

app = Ursina()
sky = Sky()

# Game + 3d map ########################################################################################################
class game_general(Entity):
    def __init__(self):
        super().__init__()
        camera.orthographic = False

        self.computer_proxy = False
        self.gui_autoriz = True
        self.in_game = False
              

        self.player = FirstPersonController()
        self.player.position = (0, 4, 0)
        self.player.gravity = 1
        self.player.jump_height = 1.5

        self.level = 0


        self.floor = Entity(model='cube', collider='box', scale=(10, 1, 10), position=(0, 0, 0), color=color.white, texture='wall.jpg')
        self.wall1 = Entity(model='cube', collider='box', scale=(10, 8, 1), position=(0, 4, 5), color=color.gray, texture='wall2.jpg')
        self.wall2 = Entity(model='cube', collider='box', scale=(10, 8, 1), position=(0, 4, -5), color=color.gray, texture='wall2.jpg')
        self.wall3 = Entity(model='cube', collider='box', scale=(10, 8, 1), position=(-5, 4, 0), color=color.gray, texture='wall2.jpg')
        self.wall4 = Entity(model='cube', collider='box', scale=(10, 8, 1), position=(5, 4, 0), color=color.gray, texture='wall2.jpg')
        self.portal = Entity(model='models_compressed/partail_deriere_porte_v1.obj', collider='mesh', scale=0.5, position=(0, 2, 4.1), rotation_z=180, rotation_y=90)
        self.wall3.rotation = (0, 90, 0)
        self.wall4.rotation = (0, 90, 0)
        
        class Porte(Entity):
            def __init__(self):
                super().__init__()
                self.ouvert = False
                self.pivot = Entity()
                self.door = Entity(model='models_compressed/porte.obj',texture='models_compressed/concept-papier-peint-motif-bois-texture.jpg',scale=1,collider='mesh', position=(0, 0, 0), parent=self.pivot)
                self.pivot.position = Vec3(-0.5, 2, 4.4) 
                self.door.position = Vec3(0.5, 0, -1)  


            def input(self, key):
                if self.door.hovered and key == 'f' and not self.ouvert:
                    self.pivot.animate('rotation_y', 90, duration=0.5)
                    self.ouvert = True
                elif self.door.hovered and key == 'f' and self.ouvert:
                    self.pivot.animate('rotation_y', 0, duration=0.5)
                    self.ouvert = False

            def destroy_door(self):
                destroy(self.door)
                destroy(self.pivot)
        
        self.doors = Porte()

    def GUI_selection(self):
        mouse.locked = False
        if self.level == 0:
            self.snake_button = Button(text='Snake', color=color.azure, highlight_color=color.cyan, scale=(0.2, 0.1), position=(0, 0.2))
            self.snake_button.on_click = self.start_snake_game
        else:
            self.snake_button = Button(text='Snake', color=color.gray, highlight_color=color.black, scale=(0.2, 0.1), position=(0, 0.2))
        
        if self.level == 1:
            self.labiryhth_button = Button(text='Labiryhth', color=color.azure, highlight_color=color.cyan, scale=(0.2, 0.1), position=(0, 0))
            self.labiryhth_button.on_click = self.start_labiryhth_game
        else:
            self.labiryhth_button = Button(text='Labiryhth', color=color.gray, highlight_color=color.black, scale=(0.2, 0.1), position=(0, 0))  

        if self.level == 2:
            self.hexa_button = Button(text='HexaGame', color=color.azure, highlight_color=color.cyan, scale=(0.2, 0.1), position=(0, -0.2))
            self.hexa_button.on_click = self.start_hexa_game
        else:
            self.hexa_button = Button(text='HexaGame', color=color.gray, highlight_color=color.black, scale=(0.2, 0.1), position=(0, -0.2))   

    def cleanup(self):
        destroy(self.snake_button)
        destroy(self.labiryhth_button)
        destroy(self.hexa_button)
        destroy(self.player)
        destroy(self.floor)
        destroy(self.wall1)
        destroy(self.wall2)
        destroy(self.wall3)
        destroy(self.wall4)
        destroy(self.portal)
        self.doors.destroy_door()

    def start_snake_game(self):
        self.cleanup()
        self.in_game = True
        self.player.speed = 5
        SnakeGame()

    def start_labiryhth_game(self):
        if self.level == 1:
            self.cleanup()
            self.in_game = True
            self.player.speed = 5
            Labiryhth()

    def start_hexa_game(self):
        if self.level == 2:
            self.cleanup()
            self.in_game = True
            self.player.speed = 5
            HexaGame()



    def update(self):
        if self.in_game == True:
                destroy(self.snake_button)
                destroy(self.labiryhth_button)
                destroy(self.hexa_button)

        if held_keys['escape']:
            quit()
        if self.level == 3:
            if self.in_game == False:
                self.player.collider = 'box'
                if self.player.intersects(self.portal).hit:
                    self.end_game = Text(text=f'Le jeu est terminé!\n Félicitation tu as réussi a sortir de la pièce !!',origin=(0, 0), scale=2, background=True)

    def input(self, key): 
        if self.gui_autoriz == True: 
            if key == 'e':
                self.gui = self.GUI_selection()
                self.gui_autoriz = False

# Mini Game ###########################################################################################################
class SnakeGame(Entity):
    def __init__(self):
        super().__init__()
        self.snake_speed = 0.5 
        self.snake = [Entity(model='cube', color=color.green, position=(0, 0, 0))]
        self.snake_direction = Vec3(1, 0, 0)
        self.food = Entity(model='cube', color=color.red, position=self.random_food_position())
        
        self.score = 0
        self.score_text = Text(text=f'Score: {self.score}', position=(-0.5, 0.4), scale=2, background=True)

        self.time_passed = 0
        self.accumulated_time = 0
        self.start_time = time.time()
        
        self.game_over = False
        self.win = False
        self.limiter = False

        camera.orthographic = True
        camera.position = (0, -1, -15)
        camera.fov = 20
        self.create_boundaries()

    def create_boundaries(self):
        boundary_thickness = 0.1
        boundary_color = color.gray
        boundaries = [
            Entity(model='quad', color=boundary_color, scale=(17, boundary_thickness, 1), position=(0, 8.5)),
            Entity(model='quad', color=boundary_color, scale=(17, boundary_thickness, 1), position=(0, -8.5)),
            Entity(model='quad', color=boundary_color, scale=(boundary_thickness, 9, 1), position=(-8.5, 0)),
            Entity(model='quad', color=boundary_color, scale=(boundary_thickness, 9, 1), position=(8.5, 0)),
        ]
        self.boundaries = boundaries

    def random_food_position(self):
        while True:
            new_position = (randint(-8, 8), randint(-8, 8), 0)
            if new_position not in [segment.position for segment in self.snake]:
                return new_position

    def update_snake(self):
        new_position = self.snake[0].position + self.snake_direction
        if self.is_collision(new_position):
            self.end_game()
            return

        if new_position == self.food.position:
            self.food.position = self.random_food_position()
            self.score += 1
            self.score_text.text = f'Score: {self.score}'
            new_segment = Entity(model='cube', color=color.green, position=new_position)
            self.snake.insert(0, new_segment)
        else:
            tail = self.snake.pop()
            tail.position = new_position
            self.snake.insert(0, tail)

        for segment in self.snake[1:]:
            if segment.position == self.snake[0].position:
                self.end_game()
                return

    def is_collision(self, position):
        if position.x < -8 or position.x > 8 or position.y < -8 or position.y > 8:
            return True
        return False

    def win_page(self):
        self.win = True
        self.game_over_text = Text(
            text=f'YOU ARE WIN!\nScore Final: {self.score}\nAppuie sur ENTER pour Continuer !',
            origin=(0, 0), scale=2, background=True)
        self.snake_direction = Vec3(0, 0, 0)
        
    def end_game(self):
        self.game_over = True
        self.game_over_text = Text(
            text=f'Game Over!\nScore Final: {self.score}\nAppuie sur ESC pour quitter\nAppuie sur R pour rejouer',
            origin=(0, 0), scale=2, background=True)
        self.snake_direction = Vec3(0, 0, 0)

    def restart_game(self):
        destroy(self.food)
        destroy(self.score_text)
        for segment in self.snake:
            destroy(segment)
        for boundary in self.boundaries:
            destroy(boundary)
        destroy(self.game_over_text)
        camera.orthographic = False
        self.__init__()

    def input(self, key):
        if self.game_over:
            if key == 'escape':
                app.quit()
            elif key == 'r':
                self.restart_game()

        if self.win == True:
            if key == 'enter':
                destroy(self.food)
                destroy(self.score_text)
                for segment in self.snake:
                    destroy(segment)
                for boundary in self.boundaries:
                    destroy(boundary)
                destroy(self.game_over_text)
                camera.orthographic = False
                game = game_general()
                game.level += 1

        if key == 'left arrow' and self.snake_direction != Vec3(1, 0, 0):
            self.snake_direction = Vec3(-1, 0, 0)
        elif key == 'right arrow' and self.snake_direction != Vec3(-1, 0, 0):
            self.snake_direction = Vec3(1, 0, 0)
        elif key == 'up arrow' and self.snake_direction != Vec3(0, -1, 0):
            self.snake_direction = Vec3(0, 1, 0)
        elif key == 'down arrow' and self.snake_direction != Vec3(0, 1, 0):
            self.snake_direction = Vec3(0, -1, 0)

    def update(self):
        if self.game_over:
            return
        
        if self.limiter == False:
            if self.score >= 40:
                self.win_page()
                self.limiter = True
                return
        
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        self.start_time = current_time
        self.accumulated_time += elapsed_time

        if self.limiter == False:
            if self.accumulated_time >= 0.04:  
                self.accumulated_time -= 0.04
                self.time_passed += 0.1
                if self.time_passed >= self.snake_speed:
                    self.time_passed = 0
                    self.update_snake()

class HexaGame(Entity):
    def __init__(self):
        super().__init__()
        self.lst_ascii = ['61', '62', '63', '64', '65', '66', '67', '68', '69', '6A','6B', '6C', '6D', '6E', '6F', '70', '71', '72', '73', '74','75', '76', '77', '78', '79', '7A']
        self.lst_alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        self.nbr_char = 8
        self.a = 0
        if self.a == 0:
            self.setup_ui()
        self.finish = False

    def generate_code(self):
        self.code = ""
        self.result = ""
        for i in range(self.nbr_char):
            index = randint(0, 9)
            self.code += self.lst_ascii[index] + " "
            self.result += self.lst_alphabet[index]
        print(f"Generated code: {self.result} {self.code}")

    def setup_ui(self):
        self.generate_code()
        self.code_text = Text(text=f"Code à déchiffré : {self.code}", position=(-0.6, 0.4), scale=2)
        self.instruction_text = Text(text="Enter the code:", position=(-0.2, 0.2), scale=2)
        self.input_field = InputField(position=(0, 0), scale=(0.5, 0.2))
        self.submit_button = Button(text="Submit", position=(0, -0.2), scale=(0.3, 0.1), on_click=self.check_code)
        self.result_text = Text(text="", position=(0, -0.4), scale=2)

    def check_code(self):
        code_entered = self.input_field.text
        if self.verifier_code(code_entered, self.result):
            self.result_text.text = "Code correct!"
            self.finish = True
            self.win_page()
        else:
            self.result_text.text = "Code incorrect."

    def verifier_code(self, code_entered, result):
        return code_entered == result
    
    def win_page(self):
        self.game_over_text = Text(
            text=f'YOU WIN!\nAppuie sur ENTER pour Continuer !',
            origin=(0, 0), scale=2, background=True)
        self.snake_direction = Vec3(0, 0, 0)

    def input(self, key):
        if self.finish == True:
            if key == 'enter':
                destroy(self.code_text)
                destroy(self.code_text)
                destroy(self.instruction_text)
                destroy(self.input_field)
                destroy(self.submit_button)
                destroy(self.result_text)
                destroy(self.game_over_text)
                camera.orthographic = False
                game = game_general()
                game.level += 3

class Labiryhth(Entity):
    def __init__(self):
        super().__init__()
        camera.orthographic = False

        self.player = FirstPersonController()
        self.player.position=(0,6,-3)
        self.player.gravity = 1
        self.player.jump_height = 1.5
        self.player.speed = 10
        self.player.collider = 'box'

        self.win = False
        self.active = True

        self.Labiryhth = Entity(model='models_compressed/labiryhth.obj', texture='brick',  scale=4, collider='mesh', position=(0,0,0))
        self.wall1 = Entity(model='cube', texture='brick',  scale=(4,8,4), collider='mesh', position=(4,4,-3))
        self.finish = Entity(model='cube', texture='brick',  scale=(4,8,4), color=color.green, collider='mesh', position=(-54,4,-49))

    def touch_finish(self):
        self.win = True
        if self.active == True:
            self.game_over_text = Text(text=f'YOU WIN!\nAppuie sur ENTER pour Continuer !', origin=(0, 0), scale=2, background=True)
            self.active = False

    def update(self):
        if self.player and self.finish and self.player.intersects(self.finish).hit:
            self.touch_finish()

    def input(self, key):
        if self.win == True:
            if key == 'enter':
                destroy(self.wall1)
                destroy(self.finish)
                destroy(self.Labiryhth)
                destroy(self.game_over_text)
                destroy(self.player)
                camera.orthographic = False
                game = game_general()
                game.level += 2



game = game_general()
app.run()