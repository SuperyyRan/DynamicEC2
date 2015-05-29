from  datetime  import  *  
import  time
import threading

from DynamicEC2.messages.sendMessage import *
from DynamicEC2.common.Task import *
from DynamicEC2.common.Message import *

try:
                import cPickle as pickle
except:
                import pickle



class NQueen(threading.Thread):
    def __init__(self, recv_task, init_row, init_col):
        threading.Thread.__init__(self)
        self.init_row = init_row
        self.init_col = init_col
        self.recv_task = recv_task
        self.n = self.recv_task.execParameter
        self.board = self.create_borad(self.n)
        self.queens = 0
        self.row_exist = [0 for i in range(self.n)] # row check queen exist
        self.col_exist = [0 for i in range(self.n)] # column check queen exist
        self.main_exist = [0 for i in range(2 * self.n - 1)] # main diagnosis check queen exist
        self.vice_exist = [0 for i in range(2 * self.n - 1)] # vice diagnosis check queen exist
        self.count = 0 # number of solution
        
    # create the n queen board
    def create_borad(self, n):
        board = [[0 for row in range(n)] for col in range(n)]
        return board
    
    # return the size of the board
    def size(self):
        return self.n
    
    # return the number of queens on the board
    def num_queens(self):
        return self.queens
    
    # check if the cell can put a queen
    def unguarded(self, row, col):
        if self.row_exist[row] == 1:
            return False
        if self.col_exist[col] == 1:
            return False
        if self.main_exist[self.n + row - col - 1] == 1:
            return False
        if self.vice_exist[row + col] == 1:
            return False
        
        return True
    
    # place a queen on the board
    def place_queen(self, row, col):
        self.board[row][col] = 1
        self.queens += 1
        self.row_exist[row] = 1
        self.col_exist[col] = 1
        self.main_exist[self.n + row - col - 1] = 1
        self.vice_exist[row + col] = 1
    
    # remove a queen from the board
    def remove_queen(self, row, col):
        self.board[row][col] = 0
        self.queens -= 1
        self.row_exist[row] = 0
        self.col_exist[col] = 0
        self.main_exist[self.n + row - col - 1] = 0
        self.vice_exist[row + col] = 0
    
    # draw the queens board
    def draw(self):
        for i in range(self.size()):
            print self.board[i]
   
    # backtracking solve the problem
    def solve(self, row, col):
        if row > self.n:
            return 
        if self.num_queens() == self.n:
            self.count += 1
            #print 'the count is: ', self.count
            #self.draw()
        else:
            for row in range(self.size()):
                if self.unguarded(row, col):
                    self.place_queen(row, col)
                    self.solve(row + 1, col + 1)
                    self.remove_queen(row, col)
    
    def run(self):
        print datetime.now()
        self.solve(self.init_row, self.init_col)
        print datetime.now()
        response = Message('Task_End', pickle.dumps(self.recv_task))
        sendMessage(['server'], pickle.dumps(response))
        print "-----task end-------"

if __name__ == '__main__':
    q = NQueen(12,0,0)
    #q.solve(0, 0)
    #q.setDaemon(True)
    q.start() 
