def binary_search(arr, left, right, x) -> int:
    """
    Generic binary search function that finds the element
    *furthest to the left* of an array.
    :param arr: Array like object.
    :param left: Most left index to start the search.
    :param right: Most right index to start the search.
    :param x: The element to search for.
    :returns: Index of the most left element found found.
    """

    while left < right:
        mid = (left + right) // 2
        if arr[mid] < x:
            left = mid + 1
        else:
            right = mid
    return left
