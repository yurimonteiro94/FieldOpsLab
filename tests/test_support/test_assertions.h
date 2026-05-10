#pragma once

#include <stdexcept>
#include <string>

namespace fieldops_test {

inline void expect_true(bool condition, const char* expression) {
    if (!condition) {
        throw std::runtime_error(
            std::string("Expectation failed: ") + expression
        );
    }
}

template <typename Actual, typename Expected>
inline void expect_eq(
    const Actual& actual,
    const Expected& expected,
    const char* actual_expression,
    const char* expected_expression
) {
    if (!(actual == expected)) {
        throw std::runtime_error(
            std::string("Expectation failed: ") +
            actual_expression +
            " == " +
            expected_expression
        );
    }
}

}

#define FIELDOPS_EXPECT_TRUE(condition) fieldops_test::expect_true((condition), #condition)

#define FIELDOPS_EXPECT_EQ(actual, expected) fieldops_test::expect_eq((actual), (expected), #actual, #expected)