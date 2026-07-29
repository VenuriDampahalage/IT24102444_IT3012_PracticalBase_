# blue circle --> agent
# orange circles --> food
# Gray blocks --> walls
# Red blocks --> opponents

# visual_grid_game.py
#Setting up the game logic class
import random # --> to pick random locations and moves
import tkinter as tk # --> to draw game window

# hold rules of the game
class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    # set up grid size
    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None, num_toxics=1):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  # Starting position of agent (x, y) 

        # creating walls
        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            # Generate some default scattered walls for a larger grid
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        # Dynamically generate random food positions avoiding walls and agent start
        self.food_positions = set() # create empty set --- to store (x,y) of food
        while len(self.food_positions) < num_food: # keeping loop until create required amount of food
            fx = random.randint(0, self.width - 1) # picking random x, within grid boundaries
            fy = random.randint(0, self.height - 1) # picking random y
            pos_tuple = (fx, fy) # bundling x and y
            if pos_tuple != (0, 0) and pos_tuple not in self.walls: # cheking food is not in agent initial position, nor wall positions
                self.food_positions.add(pos_tuple) # spot is safe and clear => add food coordinate

        #Step 2.1
        # Place toxic traps avoiding the start, walls, and food
        self.toxic_traps = set()
        while len(self.toxic_traps) < num_toxics:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            trap_pos = (tx, ty)
            if trap_pos != (0, 0) and trap_pos not in self.walls and trap_pos not in self.food_positions:
                self.toxic_traps.add(trap_pos)

        # Generate adversarial opponents
        self.opponents = [] # Create a flexible list so the opponent can move later
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]
            if tuple(op_pos) != (0, 0) and tuple(op_pos) not in self.walls and tuple(op_pos) not in self.food_positions:
                self.opponents.append(op_pos)

        self.score = 0
        self.steps = 0
        self.collision = False

    # acts like the agent's "eyes"
    def get_percept(self) -> dict:
        return {
            'agent_pos': list(self.agent_pos),
            'opponent_positions': [list(op) for op in self.opponents],
            'smells_food': tuple(self.agent_pos) in self.food_positions,
            'hit_wall': tuple(self.agent_pos) in self.walls,
            'collision': self.collision,
            'score': self.score,
            'remaining_food': len(self.food_positions),
            'smells_toxin': tuple(self.agent_pos) in self.toxic_traps,
        }

    # hits a wall --> -5 
    # lands on food --> +20 & food disappears
    def execute_action(self, action: str):
        self.steps += 1 
        new_pos = list(self.agent_pos)

        if action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)

        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        tuple_pos = tuple(self.agent_pos) # Locks agent's official new location --> check the food list
        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20

        if tuple(self.agent_pos) in self.toxic_traps:
            self.score -= 15

        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1
            elif move == 'Down' and op[1] > 0:
                op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    #game end --> if steps reach 60  or collition=True
    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision


from PIL import Image, ImageTk

#draws the game on screen
class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None, num_toxics=1):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents,
                                      custom_walls=walls, num_toxics=num_toxics)

        # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        #toxin image
        toxin_img = Image.open('./assets/toxin.png')
        toxin_img = toxin_img.resize((50, 50))
        self.toxin_image = ImageTk.PhotoImage(toxin_img)

        #opponent image
        opponent_img = Image.open('./assets/opponent001.png')
        opponent_img = opponent_img.resize((50, 50))
        self.opponent_img = ImageTk.PhotoImage(opponent_img)

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="#e9dbff" \
        "")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#350066",
                             fg="white")
        self.btn.pack(pady=5)

        self.draw_grid() 

    #This is the "Artist" function
    # Every single time agent takes a step --> redraws the entire board from scratch
    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size   # Calculates left x-coordinate of cell
                y1 = (self.env.height - 1 - y) * self.cell_size   # Calculates the top y-coordinate
                x2 = x1 + self.cell_size   # Calculates the right side of the cell
                y2 = y1 + self.cell_size   #Calculates the bottom of the cel

                color = "#e9dbff" if (x, y) not in self.env.walls else "#84a3e1"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#7D699D")

                # Only draw text if cell is large enough
                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
                                            font=("Arial", 8, "bold"))

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#eac820",
                                    outline="#eac820")

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_image(
                x1 + self.cell_size / 2,
                y1 + self.cell_size / 2,
                image=self.opponent_img)

        for ox, oy in self.env.toxic_traps:
                    offset = self.cell_size * 0.2
                    x1 = ox * self.cell_size + offset
                    y1 = (self.env.height - 1 - oy) * self.cell_size + offset
                    self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, 
                                               y1 + self.cell_size * 0.5, 
                                               fill="#593897",
                                               outline="#593897")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",
                                outline="#171958")

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                action = random.choice(['Up', 'Down', 'Left', 'Right'])
                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                self.root.after(250, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    root = tk.Tk()
    # Try a larger grid size like 12x12 with 15 food and 3 opponents!
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=1, num_toxics=10)
    root.mainloop()