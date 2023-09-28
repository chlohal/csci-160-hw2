from typing import Self, Union, Literal

Ordering = Union[Literal["Less"], Literal["More"], Literal["Equal"]]
Point = tuple[float, float]
Line = tuple[Point, Point]


def point_in_front_of_line(line: Line, point: Point) -> Ordering:
    (x1, y1), (x2, y2) = line
    x, y = point

    if x1 == x2:
        if x > x1:
            return "More"
        elif x < x1:
            return "Less"
        else:
            return "Equal"
    else:
        slope = (y1 - y2) / (x1 - x2)
        if (y - y2) > slope * (x - x2):
            return "More"
        elif (y - y2) < slope * (x - x2):
            return "Less"
        else:
            return "Equal"


def find_intersection(line_a: Line, line_b: Line) -> Union[Point, None]:
    (x1a, y1a), (x2a, y2a) = line_a
    (x1b, y1b), (x2b, y2b) = line_b

    if x1a == x2b:
        return


def split_line_segment_with_line(line: Line, segment: Line) -> list[tuple[Line, Ordering]]:
    point_a, point_b = segment
    point_a_position = point_in_front_of_line(line, point_a)
    point_b_position = point_in_front_of_line(line, point_b)

    if point_a_position == point_b_position:
        return [(segment, point_a_position)]
    else:
        intersection = find_intersection(line, segment)
        return [((point_a, intersection), point_a_position),
                ((intersection, point_b), point_b_position)
                ]


def find_axial_line_index(lines: list[Line]):
    for i, line in lines.enumerate():
        if line[0][0] == line[1][0]:
            return i
        if line[0][1] == line[1][1]:
            return i
    return 0


class Node:
    left: Self
    right: Self
    value: list[Line]

    def __init__(self, l, r, v) -> None:
        self.left = l
        self.right = r
        self.value = v


def bsp(image_lines: list[Line], start_partition_at_index: Union[int, None] = None) -> Node:
    if start_partition_at_index == None:
        start_partition_at_index = find_axial_line_index(image_lines)

    partition_line = image_lines[start_partition_at_index]

    left, right, on_partition = []

    for segment in image_lines:
        # Ignore self
        if segment == partition_line:
            on_partition += segment
            continue

        split_and_ordered = split_line_segment_with_line(
            partition_line, segment)
        for sub_segment, ordering in split_and_ordered:
            match ordering:
                case "Less": left += sub_segment
                case "More": right += sub_segment
                case "Equal": on_partition += sub_segment

    left_node = bsp(left)
    right_node = bsp(right)

    return Node(left_node, right_node, on_partition)


if __name__ == "__main__":
    image = [ () ]