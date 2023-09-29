from typing import Union, Literal

Ordering = Union[Literal["Less"], Literal["More"], Literal["Equal"]]
TreeOrdering = Union[Literal["PostOrder"], Literal["PreOrder"], Literal["InOrder"]]
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
        if intersection == None:
            raise ValueError("Couldn't find intersection")

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


def svg_of_line(line: Line, stroke_color = "black") -> str:
    (x1, y1), (x2, y2) = line

    return f'<path d="M {x1} {y1} L {x2} {y2}" style="stroke: {stroke_color}; stroke-width: 0.1"/>'


def svg_of_line_system(lines: list[Line], view_box: tuple[float, float, float, float] = (0, 0, 10, 10)) -> str:
    view_box_svg_attr = " ".join(str(n) for n in view_box)

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="{view_box_svg_attr}">'
            + "".join(svg_of_line(line) for line in lines)
            + "</svg>")


class BinarySpaceTree:
    left = None
    right = None
    value: list[Line]

    def __init__(self, l, r, v) -> None:
        self.left = l
        self.right = r
        self.value = v
    
    def lines(self, order: TreeOrdering = "InOrder") -> list[Line]:
        left_lines = []
        right_lines = []
        if self.left != None:
            left_lines = self.left.lines(order)
        if self.right != None:
            right_lines = self.right.lines(order)

        match order:
            case "InOrder": return left_lines + self.value + right_lines
            case "PostOrder": return left_lines + right_lines + self.value
            case "PreOrder": return  self.value + left_lines + right_lines
    
    def child_lines(self): 
        left_lines = []
        right_lines = []
        if self.left != None:
            left_lines = self.left.in_order_lines()
        if self.right != None:
            right_lines = self.right.in_order_lines()

        return left_lines + right_lines

    def post_order_lines(self):
        return self.lines("PostOrder")

    def pre_order_lines(self):
        return self.lines("PreOrder")
    
    def in_order_lines(self):
        return self.lines("InOrder")

    def print_in_order_repr(self):
        for line in self.in_order_lines():
            print(line)


def bsp(image_lines: list[Line], start_partition_at_index: Union[int, None] = None) -> Union[BinarySpaceTree, None]:
    if start_partition_at_index == None:
        start_partition_at_index = find_axial_line_index(image_lines)

    if len(image_lines) == 1:
        return BinarySpaceTree(None, None, image_lines)
    if len(image_lines) == 0:
        return None

    partition_line = image_lines[start_partition_at_index]

    in_front, in_behind, on_partition = [], [], []

    for segment in image_lines:
        # Ignore self
        if segment == partition_line:
            on_partition.append(segment)
            continue

        split_and_ordered = split_line_segment_with_line(
            partition_line, segment)
        for sub_segment, ordering in split_and_ordered:
            # Ignore lines like (x, y), (x, y) which only cover a single point
            if is_single_point(sub_segment):
                continue

            match ordering:
                case "Less": in_front.append(sub_segment)
                case "More": in_behind.append(sub_segment)
                case "Equal": on_partition.append(sub_segment)

    right_node = bsp(in_front)
    left_node = bsp(in_behind)

    return BinarySpaceTree(left_node, right_node, on_partition)


if __name__ == "__main__":
    import sys

    image = [((0, 0), (10, 0)),  # - top
             ((1, 0), (1, 9)),  # | left
             ((9, 0), (9, 9)),  # | right
             ((1, 8), (9, 8)),  # - bottom

             ((2, 2), (3, 3)),  # \
             ((2, 2), (2, 3)),  # |
             ((2, 3), (3, 3)),  # -
             ]

    space_tree = bsp(image, 0)
    
    if "svg" in sys.argv:
        print(svg_of_line_system(space_tree.in_order_lines(), view_box=(-1, -1, 12, 12)))
    else:
        space_tree.print_in_order_repr()
