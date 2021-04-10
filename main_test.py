def func1(index):
    index[0] += 4
    func2(index)

def func2(index):
    print(index[0])

def main():
    # func1([0])
    for i in range(-1,1):
        print(i)

if __name__ == "__main__":
    main()