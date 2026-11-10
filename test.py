import tkinter as tk



# CLASS GAMEOBJECT
# Class dasar untuk mengatur objek dalam game
class GameObject(object):

    # Menghubungkan objek dengan canvas dan item
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    # Mengambil posisi objek
    def get_position(self):
        return self.canvas.coords(self.item)

    # Menggerakkan objek berdasarkan koordinat X dan Y
    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    # Menghapus objek dari canvas
    def delete(self):
        self.canvas.delete(self.item)



# CLASS BALL
# Class untuk membuat dan mengatur bola
class Ball(GameObject):

    # Mengatur ukuran, arah, dan kecepatan bola
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 7

        # Membuat bentuk bola
        item = canvas.create_oval(
            x-self.radius, y-self.radius,
            x+self.radius, y+self.radius,
            fill="#FFD93D",
            outline="#FFFFFF",
            width=2
        )

        super().__init__(canvas, item)

    # Mengatur pergerakan dan pantulan bola
    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()

        # Memantulkan bola ketika menyentuh dinding kiri atau kanan
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1

        # Memantulkan bola ketika menyentuh bagian atas
        if coords[1] <= 0:
            self.direction[1] *= -1

        # Menghitung pergerakan bola berdasarkan arah dan kecepatan
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    # Mengatur tabrakan bola dengan objek lain
    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5

        # Jika bola bertabrakan dengan lebih dari satu objek
        if len(game_objects) > 1:
            self.direction[1] *= -1

        # Jika bola bertabrakan dengan satu objek
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()

            # Mengatur arah bola ketika mengenai sisi objek
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        # Mengurangi ketahanan brick ketika terkena bola
        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()



# CLASS PADDLE
# Class untuk membuat papan pemantul bola
class Paddle(GameObject):

    # Mengatur ukuran dan posisi awal paddle
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None

        # Membuat bentuk paddle
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='yellow')
        super(Paddle, self).__init__(canvas, item)

    # Menghubungkan bola dengan paddle
    def set_ball(self, ball):
        self.ball = ball

    # Menggerakkan paddle ke kiri atau kanan
    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()

        # Memastikan paddle tidak keluar dari batas layar
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)

            # Bola ikut bergerak jika masih menempel pada paddle
            if self.ball is not None:
                self.ball.move(offset, 0)



# CLASS BRICK
# Class untuk membuat dan mengatur balok
class Brick(GameObject):

    # Menentukan warna brick berdasarkan ketahanannya
    COLORS = {
        1: "#FF4D6D",
        2: "#FF9F1C",
        3: "#A855F7"
    }

    # Mengatur ukuran, posisi, dan ketahanan brick
    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits

        # Mengambil warna sesuai ketahanan brick
        color = Brick.COLORS[hits]

        # Membuat bentuk brick
        item = canvas.create_rectangle(
            x-self.width/2, y-self.height/2,
            x+self.width/2, y+self.height/2,
            fill=color,
            outline="#FFFFFF",
            width=1,
            tags="brick"
        )

        super().__init__(canvas, item)

    # Mengurangi ketahanan brick ketika terkena bola
    def hit(self):
        self.hits -= 1

        # Menghapus brick jika ketahanannya habis
        if self.hits <= 0:
            self.delete()

        # Mengubah warna brick jika masih memiliki ketahanan
        else:
            self.canvas.itemconfig(
                self.item,
                fill=Brick.COLORS[self.hits]
            )



# CLASS GAME
# Class utama yang mengatur seluruh permainan
class Game(tk.Frame):

    # Mengatur tampilan awal dan komponen permainan
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 610
        self.height = 400

        # Membuat area permainan dengan warna latar
        self.canvas = tk.Canvas(self, bg="#0f0f42",
                                width=self.width,
                                height=self.height,)
        self.canvas.pack()
        self.pack()

        # Menyimpan seluruh objek permainan
        self.items = {}
        self.ball = None

        # Membuat paddle di bagian bawah layar
        self.paddle = Paddle(self.canvas, self.width/2, 326)
        self.items[self.paddle.item] = self.paddle

        # Membuat susunan brick pada bagian atas layar
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 2)
            self.add_brick(x + 37.5, 70, 1)
            self.add_brick(x + 37.5, 90, 1)

        self.hud = None

        # Menyiapkan permainan
        self.setup_game()

        # Mengaktifkan keyboard untuk mengendalikan paddle
        self.canvas.focus_set()

        # Menggerakkan paddle ke kiri
        self.canvas.bind('<Left>',
                         lambda _: self.paddle.move(-10))

        # Menggerakkan paddle ke kanan
        self.canvas.bind('<Right>',
                         lambda _: self.paddle.move(10))

    # Mengatur kondisi awal permainan
    def setup_game(self):
           # Membuat bola baru
           self.add_ball()

           # Memperbarui tampilan jumlah nyawa
           self.update_lives_text()

           # Menampilkan instruksi untuk memulai permainan
           self.text = self.draw_text(300, 200,
                                      'Press Space to start')

           # Memulai permainan ketika tombol spasi ditekan
           self.canvas.bind('<space>', lambda _: self.start_game())

    # Membuat bola di atas paddle
    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()

        # Mengambil posisi tengah paddle
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5

        # Membuat bola dan menghubungkannya dengan paddle
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    # Membuat brick berdasarkan posisi dan ketahanannya
    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)

        # Menyimpan brick ke dalam daftar objek
        self.items[brick.item] = brick

    # Membuat teks pada area permainan
    def draw_text(self, x, y, text, size=25, color="#FDFA25"):
        return self.canvas.create_text(
            x, y,
            text=text,
            font=("Poppins", size, "bold italic"),
            fill=color
        )

    # Menampilkan jumlah nyawa pemain
    def update_lives_text(self):
        text = '♡: %s' % self.lives

        # Membuat teks nyawa jika belum tersedia
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)

        # Memperbarui jumlah nyawa
        else:
            self.canvas.itemconfig(self.hud, text=text)

    # Memulai permainan setelah tombol spasi ditekan
    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)

        # Melepaskan bola dari paddle
        self.paddle.ball = None

        # Menjalankan perulangan permainan
        self.game_loop()

    # Mengatur jalannya permainan secara berulang
    def game_loop(self):
        # Memeriksa tabrakan bola dengan objek lain
        self.check_collisions()

        # Menghitung jumlah brick yang masih tersisa
        num_bricks = len(self.canvas.find_withtag('brick'))

        # Menampilkan pesan menang jika semua brick habis
        if num_bricks == 0: 
            self.ball.speed = None
            self.draw_text(300, 200, 'You win!')

        # Memeriksa apakah bola jatuh melewati batas bawah layar
        elif self.ball.get_position()[3] >= self.height: 
            self.ball.speed = None

            # Mengurangi jumlah nyawa pemain
            self.lives -= 1

            # Menampilkan pesan kalah jika nyawa kurang dari nol
            if self.lives < 0:
                self.draw_text(300, 200, 'You Lose!!! Game Over!')

            # Menyiapkan permainan kembali
            else:
                self.after(1000, self.setup_game)

        # Jika permainan masih berlangsung
        else:
            # Memperbarui posisi bola
            self.ball.update()

            # Mengulang game loop setiap 50 milidetik
            self.after(50, self.game_loop)

    # Memeriksa tabrakan antara bola dan objek lain
    def check_collisions(self):
        ball_coords = self.ball.get_position()

        # Mencari objek yang bersentuhan dengan bola
        items = self.canvas.find_overlapping(*ball_coords)

        # Mengambil objek game yang mengalami tabrakan
        objects = [self.items[x] for x in items if x in self.items]

        # Menjalankan proses tabrakan bola
        self.ball.collide(objects)



# MENJALANKAN PROGRAM
# Bagian untuk membuka jendela permainan
if __name__ == '__main__':

    # Membuat jendela utama aplikasi
    root = tk.Tk()

    # Memberikan judul pada jendela game
    root.title('Udah di edit sama fairus')

    # Memanggil class Game
    game = Game(root)

    # Menjalankan aplikasi Tkinter
    game.mainloop()
