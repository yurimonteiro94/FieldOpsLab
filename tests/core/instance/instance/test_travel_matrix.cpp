#include "core/instance/instance/instance.h"
#include "tests/test_support/test_assertions.h"

#include <stdexcept>

void test_travel_matrix() {
    TravelMatrix matrix;

    matrix.location_ids = {"A", "B"};
    matrix.size = 2;
    matrix.durations = {
        0, 10,
        20, 0
    };
    matrix.distances = {
        0.0, 1.5,
        2.5, 0.0
    };

    FIELDOPS_EXPECT_EQ(matrix.duration(0, 0), 0);
    FIELDOPS_EXPECT_EQ(matrix.duration(0, 1), 10);
    FIELDOPS_EXPECT_EQ(matrix.duration(1, 0), 20);

    FIELDOPS_EXPECT_TRUE(matrix.distance(0, 1) == 1.5);
    FIELDOPS_EXPECT_TRUE(matrix.distance(1, 0) == 2.5);

    bool threw_exception = false;

    try {
        matrix.duration(2, 0);
    } catch (const std::out_of_range&) {
        threw_exception = true;
    }

    FIELDOPS_EXPECT_TRUE(threw_exception);
}