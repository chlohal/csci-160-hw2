# Homework 2

Will, Wil, Chloe
https://github.com/chlohal/cs-160-hw2

## Question 1

Our code for this question is written in a library format. The "user" is someone who is using our code-- specifically, the `bsp(image_lines, start_partition_at_index)` function.

We have some testing code designed for command-line input, but it's only for testing

### Input Format

We take take input in a `list` of `Line` objects, which are `tuple`s of two `Point`s: the start point and the end point of the line segment. A `Point` is a tuple of two `float`s, the $x$ and $y$ coordinates. In full, the input image is a `List[tuple[tuple[float, float], tuple[float, float]]]`.

The user can select the initial partition line with an optional argument.

### Output Format 

We output a `BinarySpaceTree`, which is a classic binary tree with a `list[Line]` as its value type. Each segment holds a list of the lines that define its leaf. This list will usually hold 1 segment, but in the edge case that multiple input segments are colinear, it will hold multiple. The `BinarySpaceTree` provides convenience methods to traverse the tree.

### Code Summary

Our code, in abstract, does the following:
- Take a list of line segments
- Choose a line to use in **partitioning**. If the user specifies a partitioning line, we use that; otherwise, we look for a line that is *axial* (either vertical or horizontal)
- If the list of lines is empty, return an empty node. If it only has 1 line, return a leaf with the line.
- Otherwise: split the list into segments *in front* of the partition and segments *behind* the partition.
	- Segments that cross the partition will be split into two.
- Recursively operate on the list of left segments and the list of right segments, building a node from each list.
- Return a node with the partition as a value; the front node as one side; and the behind node as the other side

## Question 2

## Question 3

With the assumption that IDs can be compared and that there is some ID that exists strictly more than 50% of the time in the input list, one can base a solution on the example of [Knuth and McIlroy's word count programs](https://www.cs.tufts.edu/~nr/cs257/archive/don-knuth/pearls-2.pdf). By modelling each ID as a word and setting $k=1$, the problem of "find the $k$ most common words in the file" becomes "find the single most common ID".

Knuth's solution may be more efficient, but his ultimate goal was *not* efficiency. It was demonstration of literate programming. Therefore, usage of his solution as a base would be detrimental to our understanding and yield an insufficient return.

We'll be using McIlroy's solution as a base, mostly for brevity but also for ease of understanding:

```bash
tr -cs A-Za-z' 
' | #Remove punctuation and empty lines
tr A-Z a-z | #Change words to lowercase
sort | #Sort list
uniq -c | #Find unique words with a count of how many times they occurred 
sort -rn | #Sort by number (count), reversed (descending)
sed ${1}q #Get first $k$ lines
```

> [!NOTE]  
> This is written in POSIX shell script. Each line is an instruction, and the pipe characters (`|`) direct the output of one line to the input of the next. The list of words is an implicit input to the first line, and the first argument, $k$ is referred to by `${1}`.
> 
> You don't need to understand it in depth, but make sure you understand what each line does on a basic level before reading further.

The adaptation and specialization of this solution for our specific problem will yield a working, efficient, 
and easy to understand algorithm.

### Simplification

First, we will remove the word separation code. Since input is already provided as a list of IDs, we don't need to process a file for words.

```diff
- tr -cs A-Za-z'
- ' |
- tr A-Z a-z |
  sort |
  uniq -c |
  sort -rn |
  sed ${1}q
```
We can also use a more efficient routine for finding the first $k$ items, since $k$ is always $1$.

```diff 
  sort |
  uniq -c |
  sort -rn |
- sed ${1}q
+ sed 1q 
```

### Specialization 

Since we're only looking for the greatest value, not the greatest $k$ values, we don't need to sort the entire list again with `sort -rn`. Instead, we can loop through and only look for the greatest value, then returning it.

```diff
  sort |
  uniq -c |
- sort -rn |
- sed 1q
+ { 
+   let max_value
+   let max_count = 0
+   for x in $input: 
+     if x[0] > max_count:
+       max_value = x[1]
+       max_count = x[0]
+   return max_value
+ }
```

> [!WARNING]  
> This is no longer POSIX shell script: it's pseudocode based on POSIX shell script.

Next, if we perform counting manually (instead of with `uniq -c`), we can use the assumption that there is a single ID that appears strictly more than 50% of the time in the input to optimize. Because the IDs are in order, there will be 1 run of identical items that is more than 50% of the length-- once we have found that run, we know that this is the most common ID, since even if every other ID is some other identical value, they won't surpass the 50%+ run. 

```diff
  sort |
- uniq -c |
  { 
+   let run_length = 0
+   let run_item
    let max_value
    let max_count = 0
    for item in $input:
+     if item != run_item:
+       run_item = item
+       run_length = 1
+     else:
+       run_length += 1
-     if x[0] > max_count:
-       max_value = x[1]
-       max_count = x[0]
+     if run_length > max_count
+       max_value = item
+       max_count = run_length
    return max_value
  }
```

The `diff` is messy, so here is the complete code for this step: 

```bash
sort |
{ 
  let run_length = 0
  let run_item
  let max_value
  let max_count = 0
  for item in $input:
    if item != run_item:
      run_item = item
      run_length = 1
    else:
      run_length += 1
    if x[0] > max_count:
      max_value = x[1]
      max_count = x[0]
    if run_length > max_count
      max_value = item
      max_count = run_length
  return max_value
}
```

### Optimization

We can, as an optimization, return early if we find the 50%+ run:

```diff 
@@ -16,5 +16,7 @@ 
      if run_length > max_count
        max_value = item
        max_count = run_length
+     if max_count > len($input)/2
+       return max_value
    return max_value
```

Further optimizations could fold the final iteration into the `sort`ing code, but that is beyond the scope of this assignment.

### Runtime Complexity and Correctness

This gives a runtime complexity of $O(\text{sort} + n)$ = $O(n \log n + n)$ = $O(n \log n)$, since an optimized comparison sort will have a time complexity of $O(n \log n)$.

The correctness is able to be derived from McIlroy's original solution for an arbitrary $k$, which is assumed to be correct. If his code is correct, and all permissible assumptions from the assignment hold, then our algorithm is correct-- our algorithm is essentially a specialized version of his.