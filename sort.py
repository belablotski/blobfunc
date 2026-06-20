def sort_v1(data):
    for i in range(len(data)):
        pmin = i
        for j in range(i+1, len(data)):
            if data[j] < data[pmin]:
                pmin = j
        tmp = data[i]
        data[i] = data[pmin]
        data[pmin] = tmp

if __name__ == "__main__":
    data = [3, 4, 1, 5]
    sort_v1(data)
    print(data)