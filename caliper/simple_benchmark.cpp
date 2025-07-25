#include <caliper/cali.h>
#include <iostream>

// Simple computation function to benchmark
double compute_sum_of_squares(int n) {
    CALI_CXX_MARK_FUNCTION;

    double result = 0.0;
    for (int i = 0; i < n; ++i) {
        result += i * i;
    }
    return result;
}

int main() {
    cali_init();

    std::cout << "Running simple benchmark...\n";

    const int n = 10000;
    double result = compute_sum_of_squares(n);
    std::cout << "Sum of squares: " << result << std::endl;

    return 0;
}