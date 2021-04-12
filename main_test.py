import numpy as np

def func1(lis):
    lis.append(3)
    print(len(lis))
    func2(lis)
    return lis

def func2(lis):
    lis.append(4)
    print(len(lis))

def main():
    arr = np.array([1,2,3])
    aar = np.array([1.,2.,3.])
    if np.array_equal(arr,aar):
        print("ggod")

if __name__ == "__main__":
    main()