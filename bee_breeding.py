from tkinter import *
from PIL import ImageTk, Image
from tkinter import messagebox
from pygame import mixer
import math
import random

class Honey_Bee_Breedings:
    base_case = {
        0: [-1, 0],
        1: [0, 1],
        2: [1, 1],
        3: [1, 0],
        4: [0, -1],
        5: [-1, -1]
    }

    def __init__(self, num1: int, num2: int):
        self.n1 = num1
        self.n2 = num2
        distance = self.distance(self.n1, self.n2)
        distance_output.delete(0, END)
        distance_output.insert(0, str(distance))

    def max_in_ring(self, ring: int) -> int:
        return 3 * ring**2 + 3 * ring + 1

    def ring_number(self, num: int) -> int:
        return math.ceil((math.sqrt((4 * num - 1) / 12.0) - 0.5))

    def num_to_coordinate(self, num: int) -> list:
        if num == 1:
            return [0, 0]

        side_length = ring = self.ring_number(num)

        ring_distance = self.max_in_ring(ring) - num

        base_number = ring_distance // side_length
        base_ring_distance =  ring_distance % side_length

        corner = self.base_case[base_number]
        next_corner = self.base_case[(base_number + 1) % 6]

        direction = [next_corner[0] - corner[0], next_corner[1] - corner[1]]

        coords = [corner[0] * ring + direction[0] * base_ring_distance , corner[1] * ring + direction[1] * base_ring_distance]

        return coords

    def coordinate_to_num(self, coord):
        if coord == [0, 0]:
            return 1

        ring = max([max(coord) - min(coord), max(map(abs, coord))])

        if coord[0] == ring:
            side = 2
        elif coord[0] == -ring:
            side = 5
        elif coord[1] == ring:
            side = 1
        elif coord[1] == -ring:
            side = 4
        elif coord[0] > coord[1]:
            side = 3
        else:
            side = 0

        max_num = self.max_in_ring(ring)
        corner = [x * ring for x in self.base_case[side]]
        ring_distance = side * ring + self.length_of_diff([coord[i] - corner[i] for i in range(2)])
        return max_num if ring_distance == ring * 6 else max_num - ring_distance

    def path_between(self):
        coord1, coord2 = self.num_to_coordinate(self.n1), self.num_to_coordinate(self.n2)
        diff = [coord1[i] - coord2[i] for i in range(2)]
        path = []

        while diff != [0, 0]:
            path.append([coord2[i] + diff[i] for i in range(2)])

            if diff[0]<0 and diff[1]<0:
                move = [1, 1]
            elif diff[0]>0 and diff[1]>0:
                move = [-1, -1]
            elif diff[0] != 0:
                move = [-1 if diff[0] > 0 else 1, 0]
            else:
                move = [0, -1 if diff[1] > 0 else 1]

            diff = [diff[i] + move[i] for i in range(2)]

        path.append(coord2)

        return path

    def length_of_diff(self, diff):
        for i in range(len(diff)):
            if diff[i] < 0:
                diff[i] *=-1

        if diff[0]>0 and diff[1]>0:
            return max(diff) 
        else:
            return max(diff) - min(diff)

    def distance(self, num1, num2):
        diff = [self.num_to_coordinate(num1)[i] - self.num_to_coordinate(num2)[i] for i in range(2)]
        return self.length_of_diff(diff)

def check_input(input_value):
    if not input_value.isdigit() or int(input_value) > 169 or int(input_value) <1:
        messagebox.showerror("Invalid Input", "Please enter a valid Cell number (1 to 169).")
        return False
    return True

def calculate_distance():
    play_click_sound()
    global cell1, cell2

    n1 = n1_input.get()
    n2 = n2_input.get()

    if not check_input(n1):
        return

    if not check_input(n2):
        return
    
    cell1 = int(n1)
    cell2 = int(n2)

    breeding_obj = Honey_Bee_Breeding(cell1, cell2)
    distance_output.delete(0, END)
    distance_output.insert(0, str(breeding_obj.distance(cell1, cell2)))

def reset_selection():
    play_click_sound()
    global cell1, cell2
    cell1 = None
    cell2 = None

    canvas.delete('all')
    draw_comb()

    n1_input.delete(0, END)
    n2_input.delete(0, END)
    distance_output.delete(0, END)

def path_to_num():
    if not check_input(n1_input.get()):
        return
    if not check_input(n2_input.get()):
        return
    
    breeding_obj = Honey_Bee_Breeding(int(n1_input.get()), int(n2_input.get()))
    path_cells = breeding_obj.path_between()
    path_nums = []
    for i in path_cells:
        path_nums.append(breeding_obj.coordinate_to_num(i))
    return path_nums

images = []
image_id = None

def highlight_cells(cell_numbers, hex_color='red3'):
    global image_id
    if not cell_numbers:
        return

    cell_highlight = cell_numbers.pop(0)
    canvas.itemconfig(f"hexagon_{cell_highlight}", fill=hex_color, width=10, outline='black')
    
    if image_id:
        canvas.delete(image_id) 
    
    bee_image = Image.open('cell_bee_image.png')  
    bee_image = bee_image.resize((40, 40))  
    photo = ImageTk.PhotoImage(bee_image)
    images.append(photo)  
    x, y = get_cell_coordinates(cell_highlight) 
    image_id = canvas.create_image(x, y, image=photo)  
    
    canvas.update()

    if cell_numbers:
        root.after(500, highlight_cells, cell_numbers, hex_color)
    
    if cell_highlight ==  int(n2_input.get()):
        n1 = int(n1_input.get())
        n2 = int(n2_input.get())
        
        showinfo(n1,n2,int(distance_output.get()),path()) 

def path():
    coordinates = path_to_num()
    path = []
    for i in range(len(coordinates)):
        path.append(str(coordinates[i]))
    return '-'.join(path)

def get_cell_coordinates(cell_number):
    hexagon_id = f"hexagon_{cell_number}"

    if canvas.find_withtag(hexagon_id):
        hexagon_coords = canvas.coords(hexagon_id)
        x_coords = hexagon_coords[::2]
        y_coords = hexagon_coords[1::2]
        center_x = sum(x_coords) / 6
        center_y = sum(y_coords) / 6
        return center_x, center_y
    else:
        return None
    
def highlight_shortest_path():
    play_click_sound()
    path_cells = path_to_num()
    if path_cells:
        highlight_cells(path_cells, hex_color='red3')

def on_hexagon_click(event, cell_num):
    play_click_sound()
    global cell1, cell2

    if cell1 is None:
        cell1 = cell_num
        canvas.itemconfig(f"hexagon_{cell_num}", fill='red3')
        n1_input.delete(0, END)
        n1_input.insert(0, str(cell_num))
    elif cell2 is None:
        cell2 = cell_num
        canvas.itemconfig(f"hexagon_{cell_num}", fill='red3')
        n2_input.delete(0, END)
        n2_input.insert(0, str(cell_num))
    
def generate_leftover_coordinates(x_diff,sign,num,ring):
    if ring==1 and sign==1:
        return [[-74,0]]
    elif ring==1 and sign!=1:
        return [[74,0]]
    
    x = (num * 37) * (ring+1) * (x_diff)
    y_start = 22 * (ring - 1)
    coordinates = []
    for i in range(ring):
        y = y_start - i * 44
        coordinates.append([x, y])

    for i in range(len(coordinates)):
        for j in range(2):
            coordinates[i][j] *= sign

    return coordinates

def generate_hexagon_coordinates(ring):
    coordinates = [[0, ring * 44]]

    for i in range(1, ring + 1):
        x = -i * 37
        y = ring * 44 - i * 22
        coordinates.append([x, y])

    if ring>1:
        l = generate_leftover_coordinates(1,1,-1,ring-1)
        coordinates.extend(l)   

    for i in range(ring, 0, -1):
        x = -i * 37
        y = -ring * 44 + i * 22
        coordinates.append([x, y])

    coordinates.append([0, -ring * 44])

    for i in range(1, ring + 1):
        x = i * 37
        y = -ring * 44 + i * 22
        coordinates.append([x, y])
    
    if ring>1:
        l = generate_leftover_coordinates(-1,-1,1,ring-1)
        coordinates.extend(l)

    for i in range(ring, 0, -1):
        x = i * 37
        y = ring * 44 - i * 22
        coordinates.append([x, y])

    for i in range(ring - 1):
        x = coordinates.pop()
        coordinates.insert(0, x)

    return coordinates

def hexagon_vertices(x, y, size):
    vertices = []
    for i in range(6):
        angle = 60 * i
        vertex_x = x + size * math.cos(math.radians(angle))
        vertex_y = y + size * math.sin(math.radians(angle))
        vertices.extend([vertex_x, vertex_y])
    return vertices

def draw_hexagon(canvas, x, y, size, number, hex_color=None):
    
    hex_color = random.choice(allowed_hex_colors)
    vertices = hexagon_vertices(x, y, size)
    hexagon = canvas.create_polygon(vertices, outline='black', fill=hex_color, tags=f"hexagon_{number}")
    canvas.create_text(x, y, text=str(number), font=("Verdana", 12, "bold"), fill='white')

    canvas.tag_bind(hexagon, "<Button-1>", lambda event, num=number: on_hexagon_click(event, num))

def draw_hexagon_with_timegap():
    global hexagon_count, hexagon_num
    max_ring = 7
    if hexagon_count < max_ring:
        hexagon_count += 1
        coordinates = generate_hexagon_coordinates(hexagon_count)

        i = 0
        for x, y in coordinates:
            bee_sound = play_bee_sound()
            root.after(i * 50, lambda x=x, y=y, num=hexagon_num: draw_hexagon(canvas, center_x + x, center_y + y, hexagon_size, num))
            hexagon_num += 1
            i += 1

        root.after(len(coordinates) * 50, draw_hexagon_with_timegap)
        bee_sound.stop()

def draw_comb():
    global hexagon_count, hexagon_num

    draw_hexagon(canvas, center_x, center_y, hexagon_size, 1)
    hexagon_count = 0
    hexagon_num = 2
    random.shuffle(allowed_hex_colors)
    draw_hexagon_with_timegap()

def showinfo(n1,n2,distance,path):
    
    result_box = Toplevel(root)
    result_box.title("HONEY BEE BREEDING DETAILS")
    result_box.config(bg="SlateBlue2")
    result_box.resizable(False, False)
    result_box.geometry(f"1000x350+{root.winfo_screenwidth() // 2 - 550}+{root.winfo_screenheight() // 2 - 200}")
    result_box.iconbitmap("bee_favicon.ico")
    
    global my_img
    img = Image.open('cute_bee_image.jpg')
    my_img = ImageTk.PhotoImage(img)
    img_label = Label(result_box, image=my_img,bg="#7a67ee")
    img_label.pack(side="right",anchor="n")

    text_label1 = Label(result_box, text=f"\nCell number 1 : {n1}",fg="black", bg='SlateBlue2', font=('Arial', 16, 'bold'))
    text_label1.pack(padx=30,pady=10,anchor="nw")

    text_label2 = Label(result_box, text=f"Cell number 2 : {n2}",fg="black",bg='SlateBlue2', font=('Arial', 16, 'bold'))
    text_label2.pack(padx=30,pady=10,anchor="nw")

    text_label3 = Label(result_box, text=f"Shortest Distance : {distance}",fg="black", bg='SlateBlue2', font=('Arial', 16, 'bold'))
    text_label3.pack(padx=30,pady=10,anchor="nw")

    text_label4 = Label(result_box, text=f"Path : {path}",fg="black", bg='SlateBlue2', font=('Arial', 16, 'bold'))
    text_label4.pack(padx=30,pady=10,anchor="nw")

    ok_button = Button(result_box, text="OK",bg="black", fg='peach puff', width=20, height=2, font=('verdana' ,16,"bold"), command = result_box.destroy)
    ok_button.pack(pady=20)

def open_main_page():
    play_click_sound()
    first_page.destroy()

def close_window():
    root.destroy()

def play_click_sound():
    sound_file = "click_sound.wav"  
    mixer.Sound(sound_file).play()

def play_bee_sound():
    bee_sound_file = "bee_sound.wav" 
    bee_sound = mixer.Sound(bee_sound_file)
    bee_sound.play()
    return bee_sound

mixer.init()
first_page = Tk()
first_page.title("Front Page")
first_page.geometry('825x500')
first_page.config(background='#000000')
first_page.attributes('-fullscreen', True)

widget_frame = Frame(first_page, bg='IndianRed4', padx=40,pady=20)
widget_frame.pack(side='left',fill='y')
test_label = Label(widget_frame, text="",bg="IndianRed4")
test_label.pack()

firstpage_label = Label(first_page, text='Welcome to Honey Bee Breeding', fg='IndianRed4', bg='black', font=('verdana', 30, 'bold'))
firstpage_label.pack(side="top",pady=45)

img = Image.open('first_page_bee.jpg')
resized_img = img.resize((820, 540))
img = ImageTk.PhotoImage(resized_img)
img_frame = Frame(first_page, bg='black')  
img_frame.pack()
img_label = Label(img_frame, image=img, bg='black')
img_label.pack()

start_button = Button(first_page, text="Start", bg='black', fg='IndianRed4', width=20, height=2, command=open_main_page, font=('verdana', 20))
start_button.pack(side="bottom",pady=30)

first_page.mainloop()

root = Tk()
root.title("Honey Bee Breeding")
root.config(background='IndianRed4')
root.attributes('-fullscreen', True)

canvas_frame = Frame(root, bg='black', highlightbackground='black', highlightthickness=1)
canvas_frame.pack(side='left', anchor="nw", padx=80, pady=50)

canvas = Canvas(canvas_frame, width=800, height=800, bg='peach puff')
canvas.pack()

center_x = 400
center_y = 380
hexagon_size = 25
hexagon_count = 0
hexagon_num = 2

allowed_hex_colors = ["#28282B","#252026","#573d2e","#B48C5B","#7A746E","goldenrod2","tan2"]
draw_comb()

cell1 = None
cell2 = None

widget_frame = Frame(root, bg='black', padx=50, pady=20)
widget_frame.pack(side='right', anchor='ne', fill='y')

text_label = Label(widget_frame, text='SHORTEST DISTANCE', fg='peach puff', bg='black', font=('Arial', 30, 'bold'))
text_label.pack(pady=10)

n1_frame = Frame(widget_frame, bg='black', pady=5)
n1_frame.pack(pady=10)
n1_label = Label(n1_frame, text='Cell number 1', fg='peach puff', bg='black')
n1_label.pack(side='left', padx=5)
n1_label.config(font=('verdana', 16))
n1_input = Entry(n1_frame, width=15,font=('verdana', 16),bg="peach puff")
n1_input.pack(side='left', ipady=10, padx=5)

n2_frame = Frame(widget_frame, bg='black', pady=5)
n2_frame.pack(pady=10)
n2_label = Label(n2_frame, text='Cell number 2', fg='peach puff', bg='black')
n2_label.pack(side='left', padx=5)
n2_label.config(font=('verdana', 16))
n2_input = Entry(n2_frame, width=15, font=('verdana', 16),bg="peach puff")
n2_input.pack(side='left', ipady=10, padx=5)

calculate_button = Button(widget_frame, text="Calculate Distance", bg='black', fg='peach puff', width=20, height=2, command=calculate_distance, font=('verdana', 16))
calculate_button.pack(pady=10)

distance_frame = Frame(widget_frame, bg='black', pady=5)
distance_frame.pack(pady=10)

distance_label = Label(distance_frame, text="Distance", fg='peach puff', bg='black')
distance_label.pack(side='left', pady=5)
distance_label.config(font=('verdana', 16))

distance_output = Entry(distance_frame, width=15, font=('verdana', 16),bg="peach puff")
distance_output.pack(side='left', ipady=10, padx=5)

trace_button = Button(widget_frame, text="TRACE THE PATH", bg='black', fg='peach puff', width=20, height=2, command=highlight_shortest_path, font=('verdana', 16))
trace_button.pack(pady=10)

reset_button = Button(widget_frame, text="RESET", bg='black', fg='peach puff', width=20, height=2, command=reset_selection, font=('verdana', 16))
reset_button.pack(pady=10)

close_button = Button(widget_frame, text="Close", bg='black', fg='peach puff', width=20, height=2, command=close_window, font=('verdana', 16))
close_button.pack(side='bottom', pady=(50, 50))

root.mainloop()
