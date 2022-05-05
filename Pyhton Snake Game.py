
from re import X
import threading
import queue        #the thread-safe queue from Python standard library

from tkinter import *
import random, time

class Gui():
    """
        This class takes care of the game's graphic user interface (gui)
        creation and termination.
    """
    def __init__(self, queue, game):
        """        
            The initializer instantiates the main window and 
            creates the starting icons for the snake and the prey,
            and displays the initial gamer score.
        """
        #some GUI constants
        scoreTextXLocation = 60
        scoreTextYLocation = 15
        textColour = "white"
        #instantiate and create gui
        self.root = Tk()
        self.root.title("Snake Game")
        

        self.canvas = Canvas(self.root, width = WINDOW_WIDTH, 
            height = WINDOW_HEIGHT, bg = BACKGROUND_COLOUR)
        self.canvas.pack()
        #create starting game icons for snake and the prey
        self.snakeIcon = self.canvas.create_line(
            (0, 0), (0, 0), fill=ICON_COLOUR, width=SNAKE_ICON_WIDTH)
        self.preyIcon = self.canvas.create_rectangle(
            0, 0, 0, 0, fill=ICON_COLOUR, outline=ICON_COLOUR)
        #display starting score of 0
        self.score = self.canvas.create_text(
            scoreTextXLocation, scoreTextYLocation, fill=textColour, 
            text='Your Score: 0', font=("Helvetica","11","bold"))
        #binding the arrow keys to be able to control the snake
        for key in ("Left", "Right", "Up", "Down"):
            self.root.bind(f"<Key-{key}>", game.whenAnArrowKeyIsPressed)




    def gameOver(self):
        """
            This method is used at the end to display a
            game over button.
        """
        gameOverButton = Button(self.canvas, text="Game Over!", 
            height = 3, width = 10, font=("Helvetica","14","bold"), 
            command=self.root.destroy)
        self.canvas.create_window(200, 100, anchor="nw", window=gameOverButton)
    

class QueueHandler():
    """
        This class implements the queue handler for the game.
    """
    def __init__(self, queue, gui):
        self.queue = queue
        self.gui = gui
        self.queueHandler()
    
    def queueHandler(self):
        '''
            This method handles the queue by constantly retrieving
            tasks from it and accordingly taking the corresponding
            action.
            A task could be: game_over, move, prey, score.
            Each item in the queue is a dictionary whose key is
            the task type (for example, "move") and its value is
            the corresponding task value.
            If the queue.empty exception happens, it schedules 
            to call itself after a short delay.
        '''
        try:
            while True:
                task = self.queue.get_nowait()
                if "game_over" in task:
                    gui.gameOver()
                elif "move" in task:
                    points = [x for point in task["move"] for x in point]
                    gui.canvas.coords(gui.snakeIcon, *points)
                elif "prey" in task:
                    gui.canvas.coords(gui.preyIcon, *task["prey"])
                elif "score" in task:
                    gui.canvas.itemconfigure(
                        gui.score, text=f"Your Score: {task['score']}")
                self.queue.task_done()
        except queue.Empty:
            gui.root.after(100, self.queueHandler)


class Game():
    '''
        This class implements most of the game functionalities.
    '''
    def __init__(self, queue):
        """
           This initializer sets the initial snake coordinate list, movement
           direction, and arranges for the first prey to be created.
        """
        self.queue = queue
        self.score = 0
        #starting length and location of the snake
        #note that it is a list of tuples, each being an
        # (x, y) tuple. Initially its size is 5 tuples.       
        self.snakeCoordinates = [(495, 55), (485, 55), (475, 55),
                                 (465, 55), (455, 55)]
        #INdex 0 is the tail not the head 
        #initial direction of the snake
        self.direction = "Left"
        self.gameNotOver = True
        self.createNewPrey()

        #Declaring varibles 
        self.X_1
        self.X_2
        self.Y_1
        self.Y_2

    def superloop(self) -> None:
        """
            This method implements a main loop
            of the game. It constantly 2enerates "move" 
            tasks to cause the constant movement of the snake.
            Use the SPEED constant to set how often the move tasks
            are generated.
        """
       
        SPEED=0.3
                        
        while self.gameNotOver:
            self.move()              #Generates a move function, which will put a move function into the queue
            time.sleep(SPEED)        # Here we sleep for the ammount of time that a new task is generated
     
    def whenAnArrowKeyIsPressed(self, e) -> None:
        """ 
            This method is bound to the arrow keys
            and is called when one of those is clicked.
            It sets the movement direction based on 
            the key that was pressed by the gamer.
            Use as is.
        """
        currentDirection = self.direction
        #ignore invalid keys
        if (currentDirection == "Left" and e.keysym == "Right" or 
            currentDirection == "Right" and e.keysym == "Left" or
            currentDirection == "Up" and e.keysym == "Down" or
            currentDirection == "Down" and e.keysym == "Up"):
            return
        self.direction = e.keysym

    def move(self) -> None:
        """ 
            This method implements what is needed to be done
            for the movement of the snake.

            It generates a new snake coordinate. 

            If based on this new movement, the prey has been 
            captured, 
            it adds a task to the queue for the updated
            score and also
            creates a new prey.

            It also calls a corresponding method to check if 
            the game should be over. 
            The snake coordinates list (representing its length 
            and position) should be correctly updated.
        """
        #Getting the new coordinate of the snake 
        NewSnakeCoordinates = self.calculateNewCoordinates()
       
        #Getting the current length of the snake 
        length=int(len(self.snakeCoordinates))
        
        #When we reach the coordinate of the prey
        New_Coord_X,New_Coord_Y=NewSnakeCoordinates

        #We generate this coordinate and then we extend the snake to have a width of 15


        """
        (X_1,Y_1)     (X_2,Y_1)

        (X_1,Y_2)     (X_2,Y_2)
        """
        
        # Cannot be just bigger than the new address because snake will be  extended to have wifth of 15 
        #Thus we take the difference of them when considering the condisitonal statements
        
        if(New_Coord_X>=self.X_1-5 and New_Coord_X<=self.X_2+5 and New_Coord_Y>=self.Y_1-5 and New_Coord_Y<=self.Y_2+5):#IF the head of the snake is at the prey's coordniate means it has eaten it 
            self.createNewPrey()                                    #Once the old prey is eaten we want to create a new prey 
            self.snakeCoordinates.append(NewSnakeCoordinates)       #We append here becapuse when teh snake eats a  prey the length increases
            self.queue.put({'move':self.snakeCoordinates})          #We also want to update the visuals of the snake on the gui 
            self.score=self.score+1                                 #We are updating the score here since we have eaten the prey     
            self.queue.put({"score":self.score})
        else:
            #If they are not equal to the coordinate of the prey then we just move back the tuples
            for i in range (length):
                if(i==length-1):#Once we reached the head of the snake we want to replace it with the new Coordinate instead 
                    self.snakeCoordinates[i]=NewSnakeCoordinates        #We replace the last index list with the new coordinate since th eindex 0 tuple is replaced 
                else :
                    self.snakeCoordinates[i]=self.snakeCoordinates[i+1]     #Swapping the coordinates , last coordinate can be ignored so we can do this 
            self.queue.put({'move':self.snakeCoordinates})
        
        self.isGameOver(NewSnakeCoordinates)        #We check if the game is over after we move 
        
            
        
      



    def calculateNewCoordinates(self) -> tuple:
        """
            This method calculates and returns the new 
            coordinates to be added to the snake
            coordinates list based on the movement
            direction and the current coordinate of 
            head of the snake.
            It is used by the move() method.    
        """
        lastX, lastY = self.snakeCoordinates[-1]       
    
        #Calculating the new coordinates based on the key pressed 
        if (self.direction=="Left"):
            return(lastX-15,lastY)

        elif (self.direction=="Right"):
            return(lastX+15,lastY)

        elif (self.direction=="Up"):
            return(lastX,lastY-15)

        elif (self.direction=="Down"):
            return(lastX,lastY+15)

        else:#If any other we nust return back the original location 
            return(lastX,lastY)

    def isGameOver(self, snakeCoordinates) -> None:
        """
            This method checks if the game is over by 
            checking if now the snake has passed any wall
            or if it has bit itself.
            If that is the case, it updates the gameNotOver 
            field and also adds a "game_over" task to the queue. 
        """
        x, y = snakeCoordinates

        #Getting the lentgh of the snake
        length =len(self.snakeCoordinates) 

        if(x>500 or x<0 or y<0 or y>300):#When we are out of bounds for the X axis 
            self.gameNotOver=False          #We set the game to over 
            self.queue.put("game_over")

        elif((x,y)in self.snakeCoordinates[0:length-2 ]):#For when snake hits itself We dont want to include the head 
            self.gameNotOver=False
            self.queue.put("game_over")
        else:#When neither the snake is out of bounds or hit itself we return the original value 
            self.gameNotOver=self.gameNotOver

        

    def createNewPrey(self) -> None:
        """ 
            This methods randomly picks an x and a y as the coordinate 
            of the new prey and uses that to calculate the 
            coordinates (x - 5, y - 5, x + 5, y + 5). 
            It then adds a "prey" task to the queue with the calculated
            rectangle coordinates as its value. This is used by the 
            queue handler to represent the new prey.                    
            To make playing the game easier, set the x and y to be THRESHOLD
            away from the walls. 
        """
        THRESHOLD = 15   #sets how close prey can be to borders
        
        #Here we are generating the random number that we will sue ot caluclate the vertices of the prey 
        randomX=random.randint(0+THRESHOLD,WINDOW_WIDTH-THRESHOLD)
        randomY=random.randint(0+THRESHOLD,WINDOW_HEIGHT-THRESHOLD)
  
        #Here we are getting the values for the vertices of the square
        self.X_1=randomX-5
        self.Y_1=randomY-5
        self.X_2=randomX+5
        self.Y_2=randomY+5
        
        """
        X_1,Y_1     X_2,Y_1

        X_1,Y_2     X_2,Y_2
        """

       #Pushing the new coordinate to the queue 
        self.queue.put({"prey":(self.X_1,self.Y_1,self.X_2,self.Y_2)})


if __name__ == "__main__":
    #some constants for our GUI
    WINDOW_WIDTH = 500           
    WINDOW_HEIGHT = 300 
    SNAKE_ICON_WIDTH = 15
    
    BACKGROUND_COLOUR = "green" 
    ICON_COLOUR = "yellow" 

    gameQueue = queue.Queue()     #instantiate a queue object using python's queue class

    game = Game(gameQueue)        #instantiate the game object

    gui = Gui(gameQueue, game)    #instantiate the game user interface
    
    QueueHandler(gameQueue, gui)  #instantiate our queue handler    
    
    #start a thread with the main loop of the game
    threading.Thread(target = game.superloop, daemon=True).start()

    #start the GUI's own event loop
    gui.root.mainloop()





    #Game over shows at the start of game 
    #Sometimes prey is not captured even if snake is at coordinate 