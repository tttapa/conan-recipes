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
    constexpr std::size_t width = simd_t::size();
    std::cout << "SIMD width: " << width << "\n";

    simd_t acc {};
    std::size_t i = 0;
    for (; i + width <= n; i += width) {
        auto va = std::datapar::unchecked_load<simd_t>(a.subspan(i));
        auto vb = std::datapar::unchecked_load<simd_t>(b.subspan(i));
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
