from typing import Union, Literal

Ordering = Union[Literal["Less"], Literal["More"], Literal["Equal"]]
Point = tuple[float, float]
Line = tuple[Point, Point]


def point_in_front_of_line(line: Line, point: Point) -> Ordering:
    (x1, _), (x2, y2) = line
    x, y = point

    if is_vertical(line):
        if x < x1:
            return "More"
        elif x > x1:
            return "Less"
        else:
            return "Equal"
    else:
        slope = get_slope(line)
        if (y - y2) > slope * (x - x2):
            return "More"
        elif (y - y2) < slope * (x - x2):
            return "Less"
        else:
            return "Equal"

def get_slope(line: Line) -> float:
    (x1, y1), (x2, y2) = line
    return (y1 - y2) / (x1 - x2)

def is_vertical(line: Line) -> bool:
    (x1, _), (x2, _) = line
    
    return x1 == x2

def are_parallel(line_a, line_b):
    if is_vertical(line_a) and is_vertical(line_b):
        return True
    
def x_coord_on_line(line: Line, x: float):
    # We only need one point & the slope
    _, (x2, y2) = line
    slope = get_slope(line)

    return slope * (x - x2) + y2

# Taken from https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines
# Modified to return None instead of raising
def find_intersection(line1: Line, line2: Line) -> Union[Point, None]:
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       return None

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y

            


def split_line_segment_with_line(line: Line, segment: Line) -> list[tuple[Line, Ordering]]:
    point_a, point_b = segment
    point_a_position = point_in_front_of_line(line, point_a)
    point_b_position = point_in_front_of_line(line, point_b)

    if point_a_position == point_b_position:
        return [(segment, point_a_position)]
    else:
        intersection = find_intersection(line, segment)
        if intersection == None: raise ValueError("Couldn't find intersection")

        return [((point_a, intersection), point_a_position),
                ((intersection, point_b), point_b_position)
                ]

def is_single_point(line: Line) -> bool:
    (x1, y1), (x2, y2) = line

    return x1 == x2 and y1 == y2

def find_axial_line_index(lines: list[Line]):
    for i, line in enumerate(lines):
        if line[0][0] == line[1][0]:
            return i
        if line[0][1] == line[1][1]:
            return i
    return 0


class BinarySpaceTree:
    left = None
    right = None
    value: list[Line]

    def __init__(self, l, r, v) -> None:
        self.left = l
        self.right = r
        self.value = v

    def print_in_order_repr(self):
        if self.left != None: self.left.print_in_order_repr()

        print(self.value)

        if self.right != None: self.right.print_in_order_repr()


def bsp(image_lines: list[Line], start_partition_at_index: Union[int, None] = None) -> Union[BinarySpaceTree, None]:
    if start_partition_at_index == None:
        start_partition_at_index = find_axial_line_index(image_lines)

    if len(image_lines) == 1:
        return BinarySpaceTree(None, None, image_lines)
    if len(image_lines) == 0:
        return None

    partition_line = image_lines[start_partition_at_index]

    left, right, on_partition = [], [], []

    for segment in image_lines:
        # Ignore self
        if segment == partition_line:
            on_partition.append(segment)
            continue

        split_and_ordered = split_line_segment_with_line(
            partition_line, segment)
        for sub_segment, ordering in split_and_ordered:
            # Ignore lines like (x, y), (x, y) which only cover a single point
            if is_single_point(sub_segment): continue

            match ordering:
                case "Less": left.append(sub_segment)
                case "More": right.append(sub_segment)
                case "Equal": on_partition.append(sub_segment)

    left_node = bsp(left)
    right_node = bsp(right)

    return BinarySpaceTree(left_node, right_node, on_partition)


if __name__ == "__main__":
    image = [ ((0, 0), (10, 0)), # - top
             ((9, 0), (9, 9)), # | right 
             ((1, 0), (0, 9)), # | left 
             ((1, 8), (9, 8)), # - bottom

             ((2, 2), (3, 3)), # \ 
             ((2, 2), (2, 3)), # |
             ((2, 3), (3, 3)), # -
            ]
    
    print("done!")

    bsp(image, 0).print_in_order_repr()