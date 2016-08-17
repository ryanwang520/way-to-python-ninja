int factorial(int x) {
  if (x <= 0) {
    return 1;
  }
  return factorial(x-1) * x;
}

void swap(int *a, int *b) {
  int temp = *a;
  *a = *b;
  *b = temp;
}
