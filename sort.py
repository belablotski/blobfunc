def sort_v1(data, key=None):
    for i in range(len(data)):
        pmin = i
        for j in range(i+1, len(data)):
            lhs = key(data[j]) if key else data[j]
            rhs = key(data[pmin]) if key else data[pmin]
            if lhs < rhs:
                pmin = j
        tmp = data[i]
        data[i] = data[pmin]
        data[pmin] = tmp

if __name__ == "__main__":
    data = [3, 4, 1, 5]
    sort_v1(data)
    print(data)