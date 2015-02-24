#!/Library/Frameworks/Python.framework/Versions/3.3/bin/python3
# N-Dimensional Tic-Tac-Toe by Thomas Lively

import curses, curses.ascii, sys

# logical representation of the n-dimensional board as a single list
class Model:
    def __init__(self, dimensions=2, size=0, players=2):
        print("{0},{1}".format(dimensions, size))
        if size < 3:
            size = dimensions+1
        self.dimensions = dimensions
        self.size = size
        if self.size < 3:
            self.size = 3
        self.players = players
        if self.players < 2 or self.players > 9:
            self.players = 2
        self.board = [0 for i in range(size**dimensions)]
        self.current_player = 1
        self.game_over = False
        self.tied_game = False
        self.moves = 0
        print("{0},{1}".format(self.dimensions, self.size))

    # makes the next player the active player
    def nextTurn(self):
        self.current_player += 1
        if self.current_player > self.players:
            self.current_player = 1
        return self.current_player

    def playAtCoordinate(self, coord):
        self.validateCoord(coord)
        self.playAtIndex(self.getIndexFromCoord(coord))

    # puts the current player's number into this index of the array then check game over
    def playAtIndex(self, index):
        self.validateIndex(index)
        if self.board[index] != 0:
            raise IllegalMoveError(index)
            return
        self.board[index] = self.current_player
        seqs = self.getSequencesFromIndex(index)
        for seq in seqs:
            n = 0
            for coord in seq:
                if self.board[self.getIndexFromCoord(coord)] == self.current_player:
                    n += 1
            if n == self.size:
                self.game_over = True
                break
        self.moves += 1
        if self.moves == self.size ** self.dimensions:
            self.tied_game = True
            self.game_over = True
            

    def getIndexFromCoord(self, coord):
        self.validateCoord(coord)
        index = 0
        for i in range(len(coord)-1,-1,-1):
            index += coord[i]*(self.size**i)
        return index

    def getCoordFromIndex(self, index):
        self.validateIndex(index)
        coord_list = []
        for i in range(self.dimensions):
            nd = self.size**(self.dimensions-1-i)
            coord_list.append(index//nd)
            index %= nd
        coord_list.reverse()
        return tuple(coord_list)

    def getSequencesFromIndex(self, index):
        return self.getSequencesFromCoord(self.getCoordFromIndex(index))

    # returns all the possible winning sequences containing this coordinate set
    def getSequencesFromCoord(self, coord):
        # from a set of indices, return a subset with elements indicated by the ones in
        # bin_rep
        def getIndexSet(indices, bin_rep):
            iset = []
            for i in range(len(indices)):
                if bin_rep[i] == "1":
                    iset.append(indices[i])
            return iset

        # given a set of indices that should be varied, return the n versions of coord
        def getVariedSequences(varying_indices):
            returned_sequences = []
            for i in range(self.size):
                new_coord = list(coord)
                for index in varying_indices:
                    if coord[index] < self.size//2:
                        new_coord[index] = i
                    else:
                        new_coord[index] = self.size-i-1
                returned_sequences.append(new_coord)
            return returned_sequences
            
        # given a set of indices that should be varied and a binary representation of
        # the direction in which they should vary, return the n versions of coord
        def getMidVariedSequences(varying_indices, vary_dir):
            returned_sequences = []
            for i in range(self.size):
                new_coord = list(coord)
                for j in range(len(varying_indices)):
                    if vary_dir[j] == "1":
                        new_coord[varying_indices[j]] = i
                    else:
                        new_coord[varying_indices[j]] = self.size-i-1
                returned_sequences.append(new_coord)
            return returned_sequences
            
        self.validateCoord(coord)
        returned_sequences = []
        # for values up to half if evenly sized, up to middle-1 if oddly sized
        for x in range(self.size//2+1):
            x2 = self.size-x-1
            all_indices = []
            for index in range(len(coord)):
                if coord[index] == x or coord[index] == x2:
                    all_indices.append(index)
            for i in range(1, 2 ** len(all_indices)):
                bin_rep = bin(i)[2:]
                while len(bin_rep) < len(all_indices):
                    bin_rep = "0" + bin_rep
                iset = getIndexSet(all_indices, bin_rep)
                if x != x2:
                    returned_sequences.append(getVariedSequences(iset))
                else:
                    for j in range(2 ** (len(iset)-1)):
                        dir_vary = bin(j)[2:]
                        while len(dir_vary) < len(iset):
                            dir_vary = "0" + dir_vary
                        mid_sequences = getMidVariedSequences(iset, dir_vary)
                        returned_sequences.append(mid_sequences)
        return returned_sequences
        
    def validateIndex(self, index):
        if index < 0 or index >= len(self.board):
            raise ValueError("Invalid index")

    def validateCoord(self, coord):
        if len(coord) != self.dimensions:
            raise ValueError("Coordinate needs " + str(self.dimensions) + " dimensions")
            return
        for i in coord:
            if i >= self.size or i < 0:
                raise ValueError("0 <= coordinate < " + str(self.size))
                return
     
    # xy pairs from high order to low order to model coordinates           
    def XYCoordToCoord(self, xy):
        coord = []
        start = 0
        if self.dimensions % 2 == 1:
            start = 1
        for i in range(start+1, len(xy), 2):
            coord.insert(0, xy[i])
        if start == 1:
            coord.insert(0, xy[0])
        for i in range(start, len(xy), 2):
            coord.insert(0, xy[i])
        return tuple(coord)

class IllegalMoveError(Exception):
    def __init__(self, index):
        self.index = index

    def __str__(self):
        return "Illegal move at index " + str(self.index)


# A view for the model. Other views might use Curses or a graphics library        
class PlainTextView():
    def __init__(self, model):
        self.model = model
        self.create()    

    # returns the divider that goes between board units of the d-th horizontal order
    def getHorizontalDivider(self, d):
        if d < 0: return
        if d == 0: return ["|"]
        if d == 1: return [" "]
        div = [" ", " "]
        for i in range(d-1):
            div.insert(1, "|")
        return div
        
    # returns the divider that goes between board units of the d-th vertical order
    def getVerticalDivider(self, d):
        if d < 0: return
        if d == 0: return ["-"]
        if d == 1: return [" "]
        div = [" ", " "]
        for i in range(d-1):
            div.insert(1, "-")
        return div
    
    # recursively create the board as a matrix of characters
    def createMatrix(self, d):
        if d < 0: return
        if d == 0: return [["X"]]
        
        sub_block = self.createMatrix(d-1)
        returned = []
        
        if d % 2 == 1:
            divider = self.getHorizontalDivider(d // 2)
            for row in sub_block:
                new_row = []
                for char in row:
                    new_row.append(char)
                for i in range(self.model.size - 1):
                    for char in divider:
                        new_row.append(char)
                    for char in row:
                        new_row.append(char)
                returned.append(new_row)
            return returned
        
        if d % 2 == 0:
            divider = self.getVerticalDivider(d // 2 - 1)
            for row in sub_block:
                new_row = []
                for char in row:
                    new_row.append(char)
                returned.append(new_row)
            for i in range (self.model.size - 1):
                for char in divider:
                    new_row = []
                    for j in range(len(sub_block[0])):
                        new_row.append(char)
                    returned.append(new_row)
                for row in sub_block:
                    new_row = []
                    for char in row:
                        new_row.append(char)
                    returned.append(new_row)
            return returned
            
    # use the matrix of characters that make up the board to create maps from the
    # representation's indices to the models and vice versa, and create an str
    def create(self):
        matrix = self.createMatrix(self.model.dimensions)
        self.str_rep = ""
        for row in matrix:
            for char in row:
                self.str_rep += char
            self.str_rep += "\n" 
        #print(str_rep)          
        self.model_to_view = dict()
        self.view_to_model = dict()
        model_index = 0
        for i in range(len(self.str_rep)):
            if self.str_rep[i] == "X":
                self.str_rep = self.str_rep.replace("X", " ", 1)
                self.model_to_view[model_index] = i
                self.view_to_model[i] = model_index
                model_index += 1
        
    # given char from model, return char for display
    def getDisplayChar(self, c):
        if c == 0: return " "
        if self.model.players == 2:
            if c == 1: return "X"
            if c == 2: return "O"
        return str(c)
    
    # must be called to update the view when the state of index i in the model changes
    def update(self, i):
        index = self.model_to_view[i]
        char = self.getDisplayChar(self.model.board[i])
        self.str_rep = self.str_rep[:index] + char + self.str_rep[index+1:]
    
    def __str__(self):            
        return self.str_rep


# serves as a "Main" class and controls user interface with model and view
class TextGameController():
    def __init__(self):
        dimensions = int(input("dimensions: "))
        size = int(input("size: "))
        players = int(input("players: "))
        print("creating model...")
        self.board = Model(dimensions, size, players)
        print("creating view...")
        self.view = PlainTextView(self.board)
        
        while True:
            print()
            print(self.view)
            print()
            player = "Player " + str(self.board.current_player)
            coord = self.makeMove(player + ": ")
            self.view.update(self.board.getIndexFromCoord(coord))
            if self.board.game_over:
                if self.board.tied_game:
                    print("It's a tie :(")
                    break
                print(self.view)
                print()
                print(player + " wins!")
                break
            self.board.nextTurn()
    
    # transform user input to model coordinates
    # and coordinates through necessary checks, repeating if necessary   
    def makeMove(self, prompt):
        coord = None
        while True:
            try:
                raw_in = eval("(" + input(prompt) + ")")
                coord = self.board.XYCoordToCoord(raw_in)
                print(coord)
            except Exception as e:
                print("Unrecognizable input")
                continue
            try:
                self.board.validateCoord(coord)
            except Exception as e:
                print(e)
                continue
            try:
                self.board.playAtCoordinate(coord)
                break
            except Exception as e:
                print("Illegal move!")
                continue
        return coord

class CursesController:
    def main(self, stdscr):
        model = self.model
        view = self.view
    
        def alert():
            curses.beep()
            curses.flash()
        
        uneven = model.dimensions % 2 != 0
        locked_coords = []
        selected_x = None
        selected_y = None
    
        def centerSelected():
            nonlocal selected_x, selected_y
            selected_x = model.size // 2
            selected_y = 0
            if not (len(locked_coords) == 0 and uneven):
                selected_y = model.size // 2
            
        centerSelected()
    
        def getEnclosingRectangle(coord):
            extension = range(model.dimensions - len(coord))
            min_xycoord = coord[:]
            min_xycoord.extend([0 for i in extension])
            min_coord = model.XYCoordToCoord(min_xycoord)
            max_xycoord = coord[:]
            max_xycoord.extend([model.size-1 for i in extension])
            max_coord = model.XYCoordToCoord(max_xycoord)
            min_index = view.model_to_view[model.getIndexFromCoord(min_coord)]
            min_index = min_index - str(view).count("\n",0, min_index)
            max_index = view.model_to_view[model.getIndexFromCoord(max_coord)]
            max_index = max_index - str(view).count("\n",0, max_index)
            length = str(view).find("\n")
            min_x = min_index % length
            min_y = min_index // length
            max_x = max_index % length
            max_y = max_index // length
            return (min_y,min_x,max_y,max_x)
        
        def getPlayerColor(p):
            colors = {1:4,2:1,3:2,4:3,5:5,6:6,7:7,8:5,9:7}
            return colors[((p-1)%9)+1]
        
        curses.curs_set(0)
        win = curses.newpad(str(view).count("\n")+1, str(view).find("\n")+1)
    
        for i in range(1,8):
            curses.init_pair(i,i,0)

        history = []
    
        initialized = False
    
        while not model.game_over: 
            stdscr.clear()
        
            # Title Box Outline
            stdscr.addch(0,0,curses.ACS_ULCORNER)
            stdscr.hline(0,1,curses.ACS_HLINE,curses.COLS-2)
            stdscr.addch(0,curses.COLS-1,curses.ACS_URCORNER)
            stdscr.vline(1,0,curses.ACS_VLINE,3)
            stdscr.vline(1,curses.COLS-1,curses.ACS_VLINE,3)
        
            panel_width = model.dimensions * 2 + 11
        
            # Board Area Outline
            stdscr.addch(4,0,curses.ACS_ULCORNER)
            stdscr.hline(4,1,curses.ACS_HLINE,curses.COLS-panel_width-1)
            stdscr.addch(curses.LINES-1,0,curses.ACS_LLCORNER)
            stdscr.hline(curses.LINES-1,1,curses.ACS_HLINE,curses.COLS-panel_width-1)
            stdscr.vline(5,0,curses.ACS_VLINE,curses.LINES-6)
        
            # Top Panel Box Outline
            stdscr.addch(4,curses.COLS-panel_width,curses.ACS_ULCORNER)
            stdscr.hline(4,curses.COLS-panel_width+1,curses.ACS_HLINE,panel_width-2)
            stdscr.addch(4,curses.COLS-1,curses.ACS_URCORNER)
            stdscr.vline(5,curses.COLS-panel_width,curses.ACS_VLINE,4)
            stdscr.vline(5,curses.COLS-1,curses.ACS_VLINE,4)
            stdscr.addch(9,curses.COLS-panel_width,curses.ACS_LLCORNER)
            stdscr.addch(9,curses.COLS-1,curses.ACS_LRCORNER)
            stdscr.hline(9,curses.COLS-panel_width+1,curses.ACS_HLINE,panel_width-2)
        
            # Bottom Panel OUTLINE
            stdscr.vline(10,curses.COLS-panel_width,curses.ACS_VLINE,curses.LINES-11)
            stdscr.vline(10,curses.COLS-1,curses.ACS_VLINE,curses.LINES-11)
            stdscr.addch(curses.LINES-1,curses.COLS-panel_width,curses.ACS_LLCORNER)
            stdscr.hline(curses.LINES-1,curses.COLS-panel_width+1,
                curses.ACS_HLINE,panel_width-2)
            try:stdscr.addch(curses.LINES-1,curses.COLS-1,curses.ACS_LRCORNER)
            except:pass
        
            title = "N-Dimensional Tic-Tac-Toe ({0}^{1})"\
                .format(model.size,model.dimensions)
            stdscr.addstr(2, curses.COLS//2 - len(title)//2, title)
        
     
            # Get input
            key = None
            curses.flushinp()
            if initialized:
                key = win.getch()
            else:
                initialized = True
        
            if key == ord("w"):
                if selected_y == 0 or len(locked_coords) == 0 and uneven:
                    alert()
                else:
                    selected_y -= 1
        
            if key == ord("s"):
                if selected_y == model.size-1 or len(locked_coords) == 0 and uneven:
                    alert()
                else:
                    selected_y += 1
    
            if key == ord("a"):
                if selected_x == 0:
                    alert()
                else:
                    selected_x -= 1
    
            if key == ord("d"):
                if selected_x == model.size-1:
                    alert()
                else:
                    selected_x += 1
        
            if key == ord("\n"):
                locked_coords.append(selected_x)
                if not (len(locked_coords) == 1 and uneven):
                    locked_coords.append(selected_y)
                centerSelected()
            
                if len(locked_coords) == model.dimensions:
                        try:
                            coord = model.XYCoordToCoord(locked_coords)
                            model.playAtCoordinate(coord)
                            view.update(model.getIndexFromCoord(coord))
                            history.insert(0, (model.current_player, locked_coords[:]))
                            del locked_coords[:]
                            centerSelected()
                            if not model.game_over:
                                model.nextTurn()
                        except Exception:
                            key = curses.ascii.ESC
            
            if key == curses.ascii.ESC:
                if len(locked_coords) == 0:
                    alert()
                else:
                    selected_y = locked_coords[-1]
                    del locked_coords[-1]
                    if not (len(locked_coords) == 0):
                        selected_x = locked_coords[-1]
                        del locked_coords[-1]
                    else:
                        selected_x = selected_y
                        selected_y = 0
                    
            # Draw info box contents
            info_line = "Player {0}".format(model.current_player)
            stdscr.addstr(6, round(curses.COLS-(panel_width + len(info_line))/2),
                info_line,
                curses.color_pair(getPlayerColor(model.current_player)))
            info_coord = locked_coords[:]
            info_coord.append(selected_x)
            if not (len(locked_coords) == 0 and uneven):
                info_coord.append(selected_y)
            info_line = str(info_coord)[1:-1].replace(" ", "")
            stdscr.addstr(7, round(curses.COLS-(panel_width + len(info_line))/2),
                info_line,
                curses.color_pair(getPlayerColor(model.current_player)))
        
        
            # Draw move history
            for i, move in enumerate(history):
                if 10 + i == curses.LINES -1:
                    break
                p, loc = move
                loc = str(loc)[1:-1].replace(" ", "")
                stdscr.addstr(10+i, curses.COLS-panel_width+1,
                    "Player {0}: {1}".format(p, loc),
                    curses.color_pair(getPlayerColor(p)))
        
            # Draw board
            win.addstr(0,0, str(view))
        
        
            # Highlight selected area       
            coord = locked_coords[:]
            coord.append(selected_x)
            if not (len(locked_coords) == 0 and uneven):
                coord.append(selected_y)
            min_y,min_x,max_y,max_x = getEnclosingRectangle(coord)
            for y in range(min_y, max_y+1):
                win.chgat(y, min_x, max_x + 1 - min_x,
                    curses.A_REVERSE |
                    curses.color_pair(getPlayerColor(model.current_player)))
            
            # Highlight past moves
            for p, loc in history:
                rect = getEnclosingRectangle(loc)
                current = win.inch(rect[0], rect[1])
                if current == current | curses.A_REVERSE:
                    win.chgat(rect[0], rect[1], 1, curses.color_pair(getPlayerColor(p)))
                else:
                    win.chgat(rect[0], rect[1], 1,
                        curses.color_pair(getPlayerColor(p)) | curses.A_REVERSE)
        
            # Calculate area of board to display
            pminrow = 0
            pmincol = 0
            pheight = str(view).count("\n")-1
            pwidth = str(view).find("\n")-1
            sminrow = 5
            smincol = 1
            smaxrow = curses.LINES-2
            smaxcol = curses.COLS-panel_width-1
            sheight = smaxrow - sminrow
            swidth = smaxcol - smincol
        
            if pheight <= sheight:
                dif = sheight - pheight
                sminrow += dif // 2
            else:
                pminrow1 = min_y - sheight * min_y / pheight
                pminrow2 = sheight/pheight*(pheight-max_y) + max_y - sheight
                dif1 = min_y
                dif2 = pheight - max_y
                if not (dif1 == 0 and dif2 == 0):
                    pminrow = round((pminrow1 * dif2 + pminrow2 * dif1) / (dif1 + dif2))
                else:
                    dif = sheight - pheight
                    sminrow += dif // 2
        
            if pwidth <= swidth:
                dif = swidth - pwidth
                smincol += dif // 2
            else:
                pmincol1 = min_x - swidth * min_x / pwidth
                pmincol2 = swidth/pwidth*(pwidth-max_x) + max_x - swidth
                dif1 = min_x
                dif2 = pwidth - max_x
                if not (dif1 == 0 and dif2 == 0):
                    pmincol = round((pmincol1 * dif2 + pmincol2 * dif1) / (dif1 + dif2))
                else:
                    dif = swidth - pwidth
                    smincol += dif // 2

            # Refresh the display
            stdscr.refresh()
            win.refresh(pminrow, pmincol, sminrow, smincol, smaxrow, smaxcol)
        
        
        stdscr.clear()
        win.clear() 
        if not model.tied_game:
            player = model.current_player
            message = "PLAYER {0} WINS!".format(player)
            stdscr.addstr(curses.LINES//2, round((curses.COLS - len(message))/2), message,
                curses.A_BLINK | curses.A_REVERSE | curses.color_pair(getPlayerColor(player)))
        else:
            message = "IT'S A TIE :("
            stdscr.addstr(curses.LINES//2, round((curses.COLS - len(message))/2), message,
                curses.A_BLINK | curses.A_REVERSE)
        stdscr.getch()
        
    def __init__(self, model):
        self.model = model
        self.view = PlainTextView(self.model)
        curses.wrapper(self.main)
        
# run the game if run as a script
if __name__ == "__main__":      
    #TextGameController()
    args = [int(i) for i in sys.argv[1:]]
    if args:
        CursesController(Model(*args))
    else:
        CursesController(Model(4))
