import random


def increment_until_threshold(values, threshold):
    reached_threshold_indices = []
    below_threshold = set(range(len(values)))

    while below_threshold:
        index = random.choice(list(below_threshold))
        values[index] += 1

        if values[index] >= threshold:
            below_threshold.remove(index)
            reached_threshold_indices.append(index)

    return reached_threshold_indices


# Example usage
values = [0, 0, 0, 0]
threshold = 5
order_of_reaching_threshold = increment_until_threshold(values, threshold)

print("Final values:", values)
print("Order of indices reaching the threshold:", order_of_reaching_threshold)
