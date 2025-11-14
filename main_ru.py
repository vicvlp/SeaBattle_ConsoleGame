"""
Python 3.7+

Морской бой (консольная версия)

Классическая игра "Морской бой" для игры против компьютера.

Особенности реализации:
- Доска 6x6 клеток
- Флот: 1 корабль на 3 клетки, 2 на 2 клетки, 4 на 1 клетку
- Автоматическая расстановка кораблей
- Визуальное отображение доски с использованием Unicode-символов
- Система исключений для обработки ошибок ввода

Классы:
- Dot: представление точки на доске
- Ship: корабль с определенной длиной и ориентацией  
- Board: игровая доска с логикой размещения кораблей и стрельбы
- Player, User, AI: классы игроков
- Game: управление игровым процессом

Для выхода из игры введите 'stop' вместо координат.

Автор: Viktor Pichugin (Виктор Пичугин) | hsdpa08@gmail.com | vicvlp@mail.ru
Версия: 1.0
"""

import random

# Классы исключений для обработки ошибок в игре
class BoardException(Exception):
    """Базовый класс для исключений игровой доски"""
    pass

class BoardOutException(BoardException):
    """Исключение для выстрела за пределы доски"""
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределы доски!"

class BoardUsedException(BoardException):
    """Исключение для выстрела в уже использованную клетку"""
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"

class BoardWrongShipException(BoardException):
    """Исключение для некорректного размещения корабля"""
    pass

# Класс для представления точки на доске
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        """Переопределение равенства точек для удобства сравнения"""
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        """Строковое представление точки для отладки"""
        return f"Dot({self.x}, {self.y})"

# Класс корабля
class Ship:
    def __init__(self, bow, length, orientation):
        """
        Инициализация корабля
        :param bow: точка носа корабля (Dot)
        :param length: длина корабля
        :param orientation: ориентация (0 - горизонтальная, 1 - вертикальная)
        """
        self.bow = bow
        self.length = length
        self.orientation = orientation
        self.lives = length
    
    @property
    def dots(self):
        """Возвращает список всех точек корабля"""
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y
            
            if self.orientation == 0:
                cur_x += i
            elif self.orientation == 1:
                cur_y += i
            
            ship_dots.append(Dot(cur_x, cur_y))
        
        return ship_dots
    
    def shooten(self, shot):
        """Проверка попадания в корабль"""
        return shot in self.dots

# Класс игровой доски
class Board:
    _EMPTY_SIGN = "\u25A1"    # Пустое игровое поле. "\u25A1" - символ пустого квадрата в юникоде
    _SHIP_SIGN = "\u25A0"     # Клетка с кораблём (частью корабля). "\u25A0" - символ квадрата в юникоде
    _CONTOUR_SIGN = "\u00B7"  # Контур вокруг уничтоженных кораблей. "\u00B7" - символ точки по центру в юникоде
    _HIT_SIGN = "\u2573"      # Обозначение попадания по кораблю (части корабля). "\u2573" - символ диагонального креста в юникоде
    _LOSE_SIGN = "\u25CF"     # Обозначение промаха. "\u25CF" символ заполненного круга в юникоде 

    def __init__(self, hid=False):
        self.field = [[self._EMPTY_SIGN] * 6 for _ in range(6)]  # Начальное заполнение игрового поля
        self.ships = []
        self.hid = hid
        self.live_ships = 0
        self.busy_dots = []  # Занятые точки (корабли + границы)
        self.shot_dots = []  # Точки, в которые уже стреляли
    
    def __str__(self):
        """Графическое представление доски"""
        res = "    | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1}   | " + " | ".join(row) + " |"
        
        if self.hid:
            # Заменяем символы кораблей на пустые клетки если скрываем доску
            res = res.replace(self._SHIP_SIGN, self._EMPTY_SIGN)
        
        return res
    
    def out(self, dot):
        """Проверка выхода точки за границы доски"""
        return not ((0 <= dot.x < 6) and (0 <= dot.y < 6))  # Возврат True если за пределами; False если внутри
    
    def contour(self, ship, verb=False):
        """Отмечает контур корабля на доске"""
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        for d in ship.dots:  # Проход по всем точкам корабля
            for dx, dy in near:  # Перебор всех сдвигов (для вычисления контура) точек корабля
                cur = Dot(d.x + dx, d.y + dy)  # Текущая рассматриваемая точка контура корабля

                if verb:  # Если корабль уничтожен
                    # Используем символ в self._CONTOUR_SIGN для обозначения контура при уничтожении корабля
                    # Если координаты не за пределами игрового поля 
                    # и в этом месте не символ попадания и не символ промаха (чтоб не затирать)
                    if not self.out(cur) \
                        and (self.field[cur.y][cur.x] != self._HIT_SIGN) \
                        and (self.field[cur.y][cur.x] != self._LOSE_SIGN):
                        self.field[cur.y][cur.x] = self._CONTOUR_SIGN  # Контур вокруг уничтоженных кораблей

                # Если точка не выходит за границы поля и не в списке занятых
                if not self.out(cur) and cur not in self.busy_dots:  
                    self.busy_dots.append(cur)
    
    def add_ship(self, ship):
        """Добавление корабля на доску"""
        for d in ship.dots:
            if self.out(d) or d in self.busy_dots:
                raise BoardWrongShipException()
        
        for d in ship.dots:
            self.field[d.y][d.x] = self._SHIP_SIGN  # Обозначение клетки с кораблём (частью корабля)
            self.busy_dots.append(d)
        
        self.ships.append(ship)
        self.contour(ship)
        self.live_ships += 1
    
    def shot(self, dot):
        """Осуществление выстрела по доске"""
        if self.out(dot):
            raise BoardOutException()
        
        if dot in self.shot_dots:
            raise BoardUsedException()
        
        self.shot_dots.append(dot)
        
        for ship in self.ships:
            if dot in ship.dots:
                ship.lives -= 1
                self.field[dot.y][dot.x] = self._HIT_SIGN  # Обозначение попадания по кораблю (части корабля)
                
                if ship.lives == 0:  # Если жизни у текущего корабля закончились
                    self.live_ships -= 1  # Уменьшить общее количество оставшихся кораблей
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return True
                else:
                    print("Корабль ранен!")
                    return True
        
        self.field[dot.y][dot.x] = self._LOSE_SIGN  # Обозначение промаха
        print("Промах!")
        return False

# Базовый класс игрока
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy
    
    def ask(self):
        """Абстрактный метод для запроса хода"""
        raise NotImplementedError()
    
    def move(self):
        """Осуществление хода игрока"""
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

# Класс игрока-компьютера
class AI(Player):
    def ask(self):
        """Случайный выбор точки для выстрела"""
        # Учёт и действия при попаданиях в этой версии не реализованы
        d = Dot(random.randint(0, 5), random.randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d

# Класс игрока-пользователя
class User(Player):
    def ask(self):
        """Запрос координат выстрела у пользователя"""
        while True:
            try:
                coords = input("Ваш ход (формат: x y): ").strip()
                
                if coords.lower() == "stop":
                    print("Игра завершена. Спасибо за игру!")
                    exit(0)  # Немедленный выход
                
                x, y = map(int, coords.split())
                if not (1 <= x <= 6 and 1 <= y <= 6):
                    print("Координаты должны быть от 1 до 6!")
                    continue

                return Dot(x-1, y-1)
            except ValueError:
                print("Введите два числа через пробел!")

# Основной класс игры
class Game:
    def __init__(self):
        user_board = self.random_board()
        ai_board = self.random_board()
        ai_board.hid = True
        
        self.user = User(user_board, ai_board)
        self.ai = AI(ai_board, user_board)
    
    def random_board(self):
        """Генерация случайной доски с кораблями"""
        board = None
        while board is None:
            board = self.try_generate_board()
        return board
    
    def try_generate_board(self):
        """Попытка генерации доски с кораблями"""
        lens = [3, 2, 2, 1, 1, 1, 1]  # Длины кораблей
        board = Board()
        attempts = 0
        
        for length in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None  # Слишком много попыток - начать заново
                
                ship = Ship(
                    Dot(random.randint(0, 5), random.randint(0, 5)),
                    length,
                    random.randint(0, 1)
                )
                try:
                    print(f"Test {ship.dots}")
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        return board
    
    def draw_boards(self):
        """Отображение игровых полей"""
        print("-" * 20)
        print("Доска пользователя:")
        print(self.user.board)
        print("-" * 20)
        print("Доска компьютера:")
        print(self.ai.board)

    def greet(self):
        """Приветствие и правила игры"""
        print("-------------------")
        print("  Добро пожаловать  ")
        print("      в игру       ")
        print("   Морской бой!    ")
        print("-------------------")
        print(" Формат ввода: x y ")
        print(" x - номер столбца ")
        print(" y - номер строки  ")
    
    def loop(self):
        """Основной игровой цикл"""
        num = 0
        while True:
            self.draw_boards()
            
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.user.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                input('Нажмите "Ввод" для хода компьютера')  # Для большего контроля за ходом игры
                repeat = self.ai.move()
            
            if repeat:
                num -= 1  # Повтор хода при попадании
            
            if self.ai.board.live_ships == 0:
                self.draw_boards()  # Финальное отображение игровых полей
                print("-" * 20)
                print("Пользователь выиграл!")
                break
            
            if self.user.board.live_ships == 0:
                self.draw_boards()  # Финальное отображение игровых полей
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            
            num += 1
    
    def start(self):
        """Запуск игры"""
        self.greet()
        self.loop()

# Запуск игры
if __name__ == "__main__":
    g = Game()
    g.start()