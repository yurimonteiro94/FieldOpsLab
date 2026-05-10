#include "core/instance/instance_validator/instance_validator.h"
#include "core/io/instance_json_loader/instance_json_loader.h"
#include "tests/test_support/test_assertions.h"

void test_instance_validator() {
    Instance instance =
        load_instance_from_json("data/instances/sample_instance_001.json");

    ValidationResult result = validate_instance(instance);

    FIELDOPS_EXPECT_TRUE(result.is_valid());
    FIELDOPS_EXPECT_EQ(result.errors.size(), 0);
}