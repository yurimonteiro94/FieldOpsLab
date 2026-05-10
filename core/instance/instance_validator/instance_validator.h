#pragma once

#include <string>
#include <vector>

#include "core/instance/instance/instance.h"

struct ValidationResult {
    std::vector<std::string> errors;
    std::vector<std::string> warnings;

    bool is_valid() const;
};

ValidationResult validate_instance(const Instance& instance);

void print_validation_result(const ValidationResult& result);