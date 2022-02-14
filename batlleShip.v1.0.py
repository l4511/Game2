from random import randint


class Dot:  # class dot
    def __init__(self, x, y):  # coord x ,y
        self.x = x
        self.y = y

    def __eq__(self, other):  # metod dliy sravnenia poley
        return self.x == other.x and self.y == other.y

    def __repr__(self):  # vivodit (x,y)
        return f"({self.x}, {self.y})"


class BoardException(Exception):  # ?
    pass


class BoardOutException(BoardException):  # oshibka, korabl za doskoy
    def __str__(self):
        return "Перелёт,целься точнее!"


class BoardUsedException(BoardException):  # oshibka, povtorniy vistrel v tochku
    def __str__(self):
        return "А говорят снаряд в одну точку дважды не бьёт, либо сюда стрелять не надо"


class BoardWrongShipException(BoardException):  # oshibka, nepravilnaia rastanovka korablia
    def __str__(self):
        return "Уточните диспозицию корабля"


class Ship:  # class korabl.
    def __init__(self, position, length, course):
        self.position = position  # position= nos korably x /y
        self.length = length  # length-dlina
        self.course = course  # course:x/y
        self.powerpoint = length  # powerpoint-jizn=dlina

    @property
    def dots(self):  # metod dots
        ship_dots = []  # list ship dots
        for i in range(self.length):  # i proxodit v range dlini korablia
            current_x = self.position.x  # znachenie position X nachinaia s nosa
            current_y = self.position.y  # znachenie position Y nachinaia s nosa

            if self.course == 0:  # esli napravlenie == 0
                current_x += i  # po osi X dobavliaem 1

            elif self.course == 1:  # esli napravlenie == 1
                current_y += i  # po osi Y dobavliaem 1

            ship_dots.append(Dot(current_x, current_y))  # dobavliaet x,y v spisok tochek korablia

        return ship_dots

    def shooten(self, shot):  #
        return shot in self.dots  #


class Board:  # class pole
    def __init__(self, hide=False, size=6):  # hide - videt pole protivnika    size-razmer polia
        self.size = size  #
        self.hide = hide  #

        self.count = 0  # schetchik 

        self.field = [["?"] * size for _ in range(size)]  # sozdaet igrovoe pole

        self.busy = []  # list busy points
        self.ships = []  # list ships on board

    def add_ship(self, ship):  # metod dobavlenia korablia na pole

        for point in ship.dots:  # proverka mojno li stavit tochku
            if self.out(point) or point in self.busy:
                raise BoardWrongShipException()  # iscluchenie esli tochka zaniata ili za polem
        for point in ship.dots:
            self.field[point.x][point.y] = "■"  # stavit metku korablia na pole
            self.busy.append(point)  # dobavliaet tochku v spisok zaniatix tochek

        self.ships.append(ship)  # dobavliae korabl v spisok korabley na doske
        self.contour(ship)  #

    def contour(self, ship, verb=False):  # sozdaet kontur korablia
        around = [  # spisok tochek dly sozdania kontura
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for point in ship.dots:
            for pointx, pointy in around:
                current = Dot(point.x + pointx, point.y + pointy)  # sozdaetsy kontur ispolzua popravki iz around
                if not (self.out(current)) and current not in self.busy:
                    if verb:
                        self.field[current.x][current.y] = "☼"  # stavit simvol v konturnuu oblast
                    self.busy.append(current)  # dobavliaet tochki kontura v spisok zaniatix tochek

    def __str__(self):  
        res = ""  
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"  
        for i, row in enumerate(self.field):  
            res += f"\n{i + 1} | " + " | ".join(row) + " |"  

        if self.hide:  
            res = res.replace("■", "?")  
        return res

    def out(self, point):  # metod dly proverki togo chto tochka na pole
        return not ((0 <= point.x < self.size) and (0 <= point.y < self.size))  

    def shot(self, point):  # vistrel i proverka na iskluchenia
        if self.out(point):
            raise BoardOutException()

        if point in self.busy:
            raise BoardUsedException()

        self.busy.append(point)  # esli vistrel proxodit proverku -dobavliaetsy v spisok zaniatix tochek

        for ship in self.ships:
            if point in ship.dots:
                ship.powerpoint -= 1
                self.field[point.x][point.y] = "✶"  # unichtojennaia chast korablia
                if ship.powerpoint == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Цель уничтожена!")  #
                    return False
                else:
                    print("Прямое попадание!")  #
                    return True

        self.field[point.x][point.y] = "☼"
        print("Мимо,сделай поправку!")  #
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        point = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход противника: {point.x + 1} {point.y + 1}")
        return point


class User(Player):
    def ask(self):
        while True:
            cords = input("Цельсь: ").split()

            if len(cords) != 2:
                print(" Введите координаты обстрела! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        gamer = self.random_board()
        enemy = self.random_board()
        enemy.hide = True

        self.ai = AI(enemy, gamer)
        self.us = User(gamer, enemy)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):  # privetstvie
        print("-------------------")  #
        print("  Добро пожаловать  ")  #
        print("      в игру       ")  #
        print('"    морской бой    "')  #
        print("-------------------")  #
        print(" формат ввода: x y ")  #
        print(" x - номер строки  ")  #
        print(" y - номер столбца ")  #

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


game = Game()
game.start()
