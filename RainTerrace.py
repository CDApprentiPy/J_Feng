# Python Algo: Given an array, return how many "buckets" of rain it would produce.
def rainTerrace(arr):
  current = arr[0]
  rain = 0
  pRain = 0
  for index in range(1, len(arr)):
    if arr[index] > current:
      rain += pRain
      pRain = 0
      current = arr[index]
    elif arr[index] < current:
      pRain += current - arr[index]
    elif arr[index] == current:
      pRain += current - arr[index]
      rain += pRain
      pRain = 0
  print rain 
  return rain
  
rainTerrace([1,2,3,2,1,4,3,2,3,4,1,2,3,4])