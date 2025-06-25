#include <simd>

#include <cassert>
#include <cstdlib>
#include <iostream>
#include <numeric>
#include <span>
#include <vector>

double dot(std::span<const double> a, std::span<const double> b) {
    assert(a.size() == b.size());
    const size_t n = a.size();
    using simd_t = std::datapar::simd<double>;
    constexpr std::size_t simd_width = simd_t::size();
    std::cout << "SIMD width: " << simd_width << "\n";

    simd_t acc {};
    std::size_t i = 0;
    for (; i + simd_width <= n; i += simd_width) {
        simd_t va(a.subspan(i).first<simd_width>());
        simd_t vb(b.subspan(i).first<simd_width>());
        acc += va * vb;
    }
    double result = reduce(acc);
    for (; i < n; ++i)
        result += a[i] * b[i];
    return result;
}

int main() {
    std::vector<double> a(131), b(131);
    std::iota(a.begin(), a.end(), long {+42});
    std::iota(b.begin(), b.end(), long {-42});
    auto d1 = dot(a, b);
    auto d2 = std::inner_product(a.begin(), a.end(), b.begin(), double {0});
    std::cout << d1 << "\n" << d2 << "\n";
    return d1 == d2 ? EXIT_SUCCESS : EXIT_FAILURE;
}
