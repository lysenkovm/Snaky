class FPcs:
    def __init__(self, *xy):
        if len(xy) == 1:
            self._x, self._y = xy[0]
        elif len(xy) == 2:
            self._x, self._y = xy
        
    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.x - other.x, self.y - other.y)
        elif isinstance(other, int):
            return self.__class__(self.x - other, self.y - other)
        
    def __isub__(self, other):
        return self.__sub__(other)
    
    def __add__(self, other):
        if isinstance(other, self.__class__):
            return self.__class__(self.x + other.x, self.y + other.y)
        elif isinstance(other, int):
            return self.__class__(self.x + other, self.y + other)
    
    def __iadd__(self, other):
        return self.__add__(other)
    
    def __mul__(self, value):
        return self.__class__(self.x * value, self.y * value)
    
    def __imul__(self, value):
        return self.__mul__(value)
    
    def __floordiv__(self, value):
        return self.__class__(self.x // value, self.y // value)
    
    def __ifloordiv__(self, value):
        return self.__floordiv__(value)
    
    def __truediv__(self, value):
        return self.__floordiv__(value)

    def __itruediv__(self, value):
        return self.__truediv__(value)

    def __str__(self):
        return f'FPcs{self.xy}'
    
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, new_x):
        self._x = new_x
    
    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, new_y):
        self._y = new_y
    
    @property
    def xy(self):
        return (self.x, self.y)