import tkinter as tk
from os import system
from PIL import ImageTk, Image
import json, random
import time

data = json.loads(open("data.json", "r").read())

class game(tk.Tk):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.stop = False
        self.length = data["sinitBodyNum"]
        self.Max_Score = data["Max_Score"]
        self.headmoveX = 0
        self.headmoveY = 0
        self.firstKeyPress = False  # game will start on first key press
        self.speed = data["speed"]
        self.createBoard()
        self.bind("<Any-KeyPress>", self.turn)
        self.gameLoop()
        self.mainloop()

    def createBoard(self):
        self.geometry("{}x{}".format(data["sw"], data["sh"]))
        self.title("Snake")
        self.columnconfigure(0, weight=1)
        self.currentScore = tk.Label(self, text="Current Score: 000")
        self.currentScore.grid(column=0, row=0, padx=(5, 0), pady=(3, 0))
        self.titlelabel = tk.Label(self, text="Snake", font=("Arial BOLD", 15))
        self.titlelabel.grid(column=1, row=0, padx=(60, 50), pady=(3, 0))
        self.maxScore = tk.Label(self, text="Maximum Score: {}".format(self.Max_Score))
        self.maxScore.grid(column=3, row=0, padx=(0, 5), pady=(3, 0))
        self.head = ImageTk.PhotoImage(
            Image.open(r"resources/head.PNG").resize((25, 25), Image.ANTIALIAS)
        )
        self.body = ImageTk.PhotoImage(
            Image.open(r"resources/body.PNG").resize((25, 25), Image.ANTIALIAS)
        )
        self.ball = ImageTk.PhotoImage(
            Image.open(r"resources/ball.PNG").resize((25, 25), Image.ANTIALIAS)
        )
        self.canvas = tk.Canvas(width=data["gamew"], height=(data["gameh"]))
        self.canvas.configure(bd=3, highlightthickness=3, relief="ridge")
        self.canvas.grid(column=0, row=1, columnspan=4)
        self.canvas.create_image(
            random.randint(25, 350),
            random.randint(25,320),
            image=self.ball,
            anchor="nw",
            tag="ball",
        )
        self.canvas.create_image(
            data["sposx"], data["sposy"], image=self.head, anchor="nw", tag="head"
        )
        self.createBody(1)
        self.createBody(2)
        self.bodyPartsCount = 2

    def createBody(self, num):
        self.canvas.create_image(
            data["sposx"] + (num * data["slen"]),
            data["sposy"],
            image=self.body,
            anchor="nw",
            tag="body",
        )

    def headHitBall(self):
        ball = self.canvas.find_withtag("ball")
        head = self.canvas.find_withtag("head")
        # boundary box
        x1, y1, x2, y2 = self.canvas.bbox(head)
        item_overlap = self.canvas.find_overlapping(x1, y1, x2, y2)
        for item in item_overlap:
            # print(item, ball[0], head[0])
            if ball[0] == item:
                self.canvas.delete(ball[0])
                self.canvas.create_image(
                    random.randint(25, 350),
                    random.randint(25, 320),
                    image=self.ball,
                    anchor="nw",
                    tag="ball",
                )
                self.score += 10
                self.updateScore()

    def headHitBoundaryOrSnake(self):
        head = self.canvas.find_withtag("head")
        body = self.canvas.find_withtag("body")
        x1, y1, x2, y2 = self.canvas.bbox(head)
        item_overlap = self.canvas.find_overlapping(x1 + 3, y1 + 3, x2 - 3, y2 - 3)
        # snake itself
        for el in body:
            for item in item_overlap:
                if el == item:
                    self.stop = True
                    self.gameOver()
        # boundary
        if x1 < 6 or y1 < 6 or x2 > 390 or y2 > 350:
            self.stop = True
            self.gameOver()

    def moveSnake(self):
        body = self.canvas.find_withtag("body")
        head = self.canvas.find_withtag("head")
        obj = body + head
        i = 0
        while i < len(obj) - 1:
            bodyCoords = self.canvas.coords(obj[i])  # body
            headCoords = self.canvas.coords(obj[i + 1])  # head
            self.canvas.move(
                obj[i], headCoords[0] - bodyCoords[0], headCoords[1] - bodyCoords[1]
            )
            i += 1
        self.canvas.move(head, self.headmoveX, self.headmoveY)

    def turn(self, event=None):
        key = event.keysym
        if key == "Left" and self.headmoveX >= 0:
            self.headmoveX = -data["slen"]
            self.headmoveY = 0
            self.firstKeyPress = True
        elif key == "Right" and self.headmoveX >= 0:
            self.headmoveX = data["slen"]
            self.headmoveY = 0
            self.firstKeyPress = True
        elif key == "Up" and self.headmoveY >= 0:
            self.headmoveX = 0
            self.firstKeyPress = True
            self.headmoveY = -data["slen"]
        elif key == "Down" and self.headmoveY >= 0:
            self.headmoveX = 0
            self.headmoveY = data["slen"]
            self.firstKeyPress = True
        elif key == "Escape":
            self.destroy()
        elif key == "plus":
            self.speed += 100
        elif key == "r":
            self.retry()
        elif key == "minus":
            if self.speed > 100:
                self.speed -= 100
        else:
            pass

    def retry(self):
        self.destroy()
        self.__init__()

    def gameLoop(self):
        if self.firstKeyPress:
            self.headHitBall()
            self.headHitBoundaryOrSnake()
            if not self.stop:
                self.moveSnake()
                self.after(self.speed, self.gameLoop)
            else:
                self.gameOver()
        else:
            self.after(self.speed, self.gameLoop)

    def updateScore(self):
        self.currentScore.configure(
            text="Current Score: {}".format(str(self.score).zfill(3))
        )
        if self.score%100 == 0:
            self.bodyPartsCount += 1
            self.createBody(self.bodyPartsCount)
        if self.score >= self.Max_Score:
            self.Max_Score = self.score
            data["Max_Score"] = self.score
            self.maxScore.configure(
                text="Maximum Score: {}".format(str(data["Max_Score"]).zfill(3))
            )
            json.dump(data, open("data.json", "w"))
        else:
            self.maxScore.configure(
                text="Maximum Score: {}".format(str(data["Max_Score"]).zfill(3))
            )

    def gameOver(self):
        self.canvas.delete("all")
        self.snake_xenia = ImageTk.PhotoImage(
            Image.open(r"resources/snake_xenzia.PNG").resize(
                (380, 346), Image.ANTIALIAS
            )
        )
        self.canvas.create_image(200, 184, image=self.snake_xenia)
        self.canvas.create_text(
            195, 100, font=("Arial BOLD", 30), text="SNAKE XENZIA", fill="#F70100"
        )
        self.canvas.create_text(
            195,
            200,
            font=("Arial BOLD", 25),
            fill="white",
            text=("Your Score: {}".format(str(self.score).zfill(2))),
        )
        if self.score > self.Max_Score:
            self.canvas.create_text(
                195,
                250,
                font=("Arial BOLD", 25),
                fill="white",
                text=("It's a High Score!"),
            )


if __name__ == "__main__":
    game = game()