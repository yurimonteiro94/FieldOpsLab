#include "core/instance/instance_validator/instance_validator.h"
#include "core/io/instance_json_loader/instance_json_loader.h"
#include "tests/test_support/test_assertions.h"

void test_instance_validator() {
    Instance valid_instance =
        load_instance_from_json("data/instances/sample_instance_001.json");

    ValidationResult valid_result = validate_instance(valid_instance);

    FIELDOPS_EXPECT_TRUE(valid_result.is_valid());
    FIELDOPS_EXPECT_EQ(valid_result.errors.size(), 0);

    Instance invalid_task_location = valid_instance;
    invalid_task_location.tasks[0].location_id = "invalid_location";

    ValidationResult invalid_task_location_result =
        validate_instance(invalid_task_location);

    FIELDOPS_EXPECT_TRUE(!invalid_task_location_result.is_valid());

    Instance invalid_technician_availability = valid_instance;
    invalid_technician_availability.technicians[0].available_to =
        invalid_technician_availability.technicians[0].available_from;

    ValidationResult invalid_technician_availability_result =
        validate_instance(invalid_technician_availability);

    FIELDOPS_EXPECT_TRUE(!invalid_technician_availability_result.is_valid());

    Instance invalid_required_skill = valid_instance;
    invalid_required_skill.tasks[0].required_skills = {"advanced"};

    ValidationResult invalid_required_skill_result =
        validate_instance(invalid_required_skill);

    FIELDOPS_EXPECT_TRUE(!invalid_required_skill_result.is_valid());

    Instance invalid_latitude = valid_instance;
    invalid_latitude.locations[0].latitude = 999.0;

    ValidationResult invalid_latitude_result =
        validate_instance(invalid_latitude);

    FIELDOPS_EXPECT_TRUE(!invalid_latitude_result.is_valid());
}