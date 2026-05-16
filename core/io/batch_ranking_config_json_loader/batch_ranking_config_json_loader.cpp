#include "core/io/batch_ranking_config_json_loader/batch_ranking_config_json_loader.h"

#include "core/analysis/batch_ranking/batch_ranking_config_validator/batch_ranking_config_validator.h"

#include <cctype>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>

static std::string read_text_file(const std::string& file_path) {
    std::ifstream input(file_path);

    if (!input.is_open()) {
        throw std::runtime_error(
            "Could not open JSON file: " + file_path
        );
    }

    std::ostringstream buffer;
    buffer << input.rdbuf();

    return buffer.str();
}

static std::string make_json_key(const std::string& key) {
    return "\"" + key + "\"";
}

static std::size_t skip_whitespace(
    const std::string& text,
    std::size_t position
) {
    while (
        position < text.size() &&
        std::isspace(static_cast<unsigned char>(text[position]))
    ) {
        ++position;
    }

    return position;
}

static bool is_escaped_quote(
    const std::string& text,
    std::size_t quote_position
) {
    if (quote_position == 0) {
        return false;
    }

    int backslash_count = 0;
    std::size_t position = quote_position;

    while (position > 0) {
        --position;

        if (text[position] != '\\') {
            break;
        }

        ++backslash_count;
    }

    return (backslash_count % 2) == 1;
}

static std::string extract_json_object_after_key(
    const std::string& text,
    const std::string& key,
    bool& found
) {
    found = false;

    const std::string json_key = make_json_key(key);
    const std::size_t key_position = text.find(json_key);

    if (key_position == std::string::npos) {
        return "";
    }

    std::size_t colon_position =
        text.find(':', key_position + json_key.size());

    if (colon_position == std::string::npos) {
        throw std::runtime_error(
            "Invalid JSON object. Missing ':' after key: " + key
        );
    }

    std::size_t object_start =
        skip_whitespace(text, colon_position + 1);

    if (object_start >= text.size() || text[object_start] != '{') {
        throw std::runtime_error(
            "Invalid JSON object. Expected object after key: " + key
        );
    }

    int depth = 0;
    bool inside_string = false;

    for (std::size_t i = object_start; i < text.size(); ++i) {
        const char character = text[i];

        if (character == '"' && !is_escaped_quote(text, i)) {
            inside_string = !inside_string;
        }

        if (inside_string) {
            continue;
        }

        if (character == '{') {
            ++depth;
        } else if (character == '}') {
            --depth;

            if (depth == 0) {
                found = true;
                return text.substr(
                    object_start,
                    i - object_start + 1
                );
            }
        }
    }

    throw std::runtime_error(
        "Invalid JSON object. Object was not closed for key: " + key
    );
}

static bool try_extract_json_string_field(
    const std::string& object_text,
    const std::string& key,
    std::string& value
) {
    const std::string json_key = make_json_key(key);
    const std::size_t key_position = object_text.find(json_key);

    if (key_position == std::string::npos) {
        return false;
    }

    const std::size_t colon_position =
        object_text.find(':', key_position + json_key.size());

    if (colon_position == std::string::npos) {
        throw std::runtime_error(
            "Invalid JSON field. Missing ':' after key: " + key
        );
    }

    std::size_t value_start =
        skip_whitespace(object_text, colon_position + 1);

    if (
        value_start >= object_text.size() ||
        object_text[value_start] != '"'
    ) {
        throw std::runtime_error(
            "Invalid JSON field. Expected string for key: " + key
        );
    }

    ++value_start;

    std::string parsed_value;

    for (std::size_t i = value_start; i < object_text.size(); ++i) {
        const char character = object_text[i];

        if (character == '"' && !is_escaped_quote(object_text, i)) {
            value = parsed_value;
            return true;
        }

        if (character == '\\' && i + 1 < object_text.size()) {
            const char escaped = object_text[i + 1];

            if (escaped == '"' || escaped == '\\' || escaped == '/') {
                parsed_value.push_back(escaped);
                ++i;
                continue;
            }

            if (escaped == 'n') {
                parsed_value.push_back('\n');
                ++i;
                continue;
            }

            if (escaped == 't') {
                parsed_value.push_back('\t');
                ++i;
                continue;
            }
        }

        parsed_value.push_back(character);
    }

    throw std::runtime_error(
        "Invalid JSON string. String was not closed for key: " + key
    );
}

static bool is_number_character(char character) {
    return
        std::isdigit(static_cast<unsigned char>(character)) ||
        character == '-' ||
        character == '+' ||
        character == '.' ||
        character == 'e' ||
        character == 'E';
}

static bool try_extract_json_number_field(
    const std::string& object_text,
    const std::string& key,
    double& value
) {
    const std::string json_key = make_json_key(key);
    const std::size_t key_position = object_text.find(json_key);

    if (key_position == std::string::npos) {
        return false;
    }

    const std::size_t colon_position =
        object_text.find(':', key_position + json_key.size());

    if (colon_position == std::string::npos) {
        throw std::runtime_error(
            "Invalid JSON field. Missing ':' after key: " + key
        );
    }

    std::size_t value_start =
        skip_whitespace(object_text, colon_position + 1);

    if (
        value_start >= object_text.size() ||
        !is_number_character(object_text[value_start])
    ) {
        throw std::runtime_error(
            "Invalid JSON field. Expected number for key: " + key
        );
    }

    std::size_t value_end = value_start;

    while (
        value_end < object_text.size() &&
        is_number_character(object_text[value_end])
    ) {
        ++value_end;
    }

    const std::string number_text =
        object_text.substr(value_start, value_end - value_start);

    try {
        value = std::stod(number_text);
    } catch (...) {
        throw std::runtime_error(
            "Invalid JSON number for key: " + key
        );
    }

    return true;
}

static void apply_optional_string_field(
    const std::string& object_text,
    const std::string& key,
    std::string& target
) {
    std::string value;

    if (try_extract_json_string_field(object_text, key, value)) {
        target = value;
    }
}

static void apply_optional_number_field(
    const std::string& object_text,
    const std::string& key,
    double& target
) {
    double value = 0.0;

    if (try_extract_json_number_field(object_text, key, value)) {
        target = value;
    }
}

static BatchRankingConfig parse_ranking_config_object(
    const std::string& object_text,
    const BatchRankingConfig& base_config
) {
    BatchRankingConfig config = base_config;

    apply_optional_string_field(
        object_text,
        "ranking_config_id",
        config.ranking_config_id
    );

    apply_optional_number_field(
        object_text,
        "objective_value_weight",
        config.objective_value_weight
    );

    apply_optional_number_field(
        object_text,
        "makespan_weight",
        config.makespan_weight
    );

    apply_optional_number_field(
        object_text,
        "total_travel_time_weight",
        config.total_travel_time_weight
    );

    apply_optional_number_field(
        object_text,
        "total_service_time_weight",
        config.total_service_time_weight
    );

    apply_optional_number_field(
        object_text,
        "total_waiting_time_weight",
        config.total_waiting_time_weight
    );

    apply_optional_number_field(
        object_text,
        "late_task_count_weight",
        config.late_task_count_weight
    );

    apply_optional_number_field(
        object_text,
        "total_lateness_weight",
        config.total_lateness_weight
    );

    apply_optional_number_field(
        object_text,
        "effect_count_weight",
        config.effect_count_weight
    );

    apply_optional_number_field(
        object_text,
        "policy_should_replan_count_weight",
        config.policy_should_replan_count_weight
    );

    apply_optional_number_field(
        object_text,
        "replanning_request_count_weight",
        config.replanning_request_count_weight
    );

    apply_optional_number_field(
        object_text,
        "replanning_success_count_weight",
        config.replanning_success_count_weight
    );

    apply_optional_number_field(
        object_text,
        "replanning_applied_count_weight",
        config.replanning_applied_count_weight
    );

    validate_batch_ranking_config(config);

    return config;
}

bool try_load_batch_ranking_config_from_json_file(
    const std::string& file_path,
    BatchRankingConfig& ranking_config
) {
    const std::string text = read_text_file(file_path);

    bool found = false;

    const std::string ranking_config_object =
        extract_json_object_after_key(
            text,
            "ranking_config",
            found
        );

    if (!found) {
        validate_batch_ranking_config(ranking_config);
        return false;
    }

    ranking_config =
        parse_ranking_config_object(
            ranking_config_object,
            ranking_config
        );

    return true;
}

BatchRankingConfig load_batch_ranking_config_from_json_file_or_default(
    const std::string& file_path,
    const BatchRankingConfig& default_ranking_config
) {
    BatchRankingConfig ranking_config = default_ranking_config;

    try_load_batch_ranking_config_from_json_file(
        file_path,
        ranking_config
    );

    return ranking_config;
}