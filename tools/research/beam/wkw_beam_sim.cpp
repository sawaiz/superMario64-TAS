#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

namespace fs = std::filesystem;

constexpr std::size_t kM64HeaderSize = 0x400;
constexpr std::size_t kM64SampleCountOffset = 0x18;
constexpr int kMaxDepth = 96;
constexpr double kPi = 3.14159265358979323846;

struct Input {
    std::uint16_t buttons{};
    std::int8_t x{};
    std::int8_t y{};
};

struct Telemetry {
    int sample{};
    std::uint32_t action{};
    int actionState{};
    int actionTimer{};
    double forwardVel{};
    double verticalVel{};
    double x{};
    double y{};
    double z{};
    int facingYaw{};
    double intendedMag{};
    int intendedYaw{};
    int cameraYaw{};
    double floorHeight{};
    double floorNx{};
    double floorNy{};
    double floorNz{};
    double wallNx{};
    double wallNy{};
    double wallNz{};
};

struct PhysicsOutput {
    double forwardVel{};
    double vx{};
    double vz{};
};

struct State {
    double forwardVel{};
    double verticalVel{};
    double x{};
    double y{};
    double z{};
    double smoothPenalty{};
    double guideScore{};
    double finalScore{};
    double distance221{};
    double distance222{};
    double distance223{};
    int lastX{};
    int lastY{};
    int depth{};
    std::array<std::int8_t, kMaxDepth> pathX{};
    std::array<std::int8_t, kMaxDepth> pathY{};
};

struct StateKey {
    int x{};
    int z{};
    int vel{};

    bool operator==(const StateKey &other) const {
        return x == other.x && z == other.z && vel == other.vel;
    }
};

struct StateKeyHash {
    std::size_t operator()(const StateKey &key) const {
        std::size_t seed = static_cast<std::uint32_t>(key.x);
        seed ^= static_cast<std::uint32_t>(key.z) + 0x9e3779b9U + (seed << 6U) + (seed >> 2U);
        seed ^= static_cast<std::uint32_t>(key.vel) + 0x9e3779b9U + (seed << 6U) + (seed >> 2U);
        return seed;
    }
};

std::vector<std::string> split(const std::string &line) {
    std::vector<std::string> fields;
    std::stringstream stream(line);
    std::string field;
    while (std::getline(stream, field, ',')) {
        fields.push_back(field);
    }
    return fields;
}

template <typename T>
T parse_number(const std::string &value);

template <>
int parse_number<int>(const std::string &value) {
    return std::stoi(value);
}

template <>
std::uint32_t parse_number<std::uint32_t>(const std::string &value) {
    return static_cast<std::uint32_t>(std::stoul(value));
}

template <>
double parse_number<double>(const std::string &value) {
    return std::stod(value);
}

std::vector<Telemetry> read_telemetry(const fs::path &path) {
    std::ifstream input(path);
    if (!input) {
        throw std::runtime_error("cannot open telemetry: " + path.string());
    }
    std::string line;
    if (!std::getline(input, line)) {
        throw std::runtime_error("empty telemetry CSV");
    }
    const auto headers = split(line);
    std::unordered_map<std::string, std::size_t> column;
    for (std::size_t i = 0; i < headers.size(); ++i) {
        column[headers[i]] = i;
    }
    const std::array required = {
        "sample", "action", "action_state", "action_timer", "h_speed", "v_speed",
        "x", "y", "z", "facing_yaw", "intended_mag", "intended_yaw", "camera_yaw",
        "floor_height", "floor_nx", "floor_ny", "floor_nz", "wall_nx", "wall_ny", "wall_nz",
    };
    for (const auto *name : required) {
        if (!column.contains(name)) {
            throw std::runtime_error(std::string("telemetry is missing column: ") + name);
        }
    }

    std::vector<Telemetry> rows;
    while (std::getline(input, line)) {
        const auto fields = split(line);
        auto get = [&](const std::string &name) -> const std::string & {
            const auto index = column.at(name);
            if (index >= fields.size()) {
                throw std::runtime_error("short telemetry row");
            }
            return fields[index];
        };
        Telemetry row;
        row.sample = parse_number<int>(get("sample"));
        row.action = parse_number<std::uint32_t>(get("action"));
        row.actionState = parse_number<int>(get("action_state"));
        row.actionTimer = parse_number<int>(get("action_timer"));
        row.forwardVel = parse_number<double>(get("h_speed"));
        row.verticalVel = parse_number<double>(get("v_speed"));
        row.x = parse_number<double>(get("x"));
        row.y = parse_number<double>(get("y"));
        row.z = parse_number<double>(get("z"));
        row.facingYaw = parse_number<int>(get("facing_yaw"));
        row.intendedMag = parse_number<double>(get("intended_mag"));
        row.intendedYaw = parse_number<int>(get("intended_yaw"));
        row.cameraYaw = parse_number<int>(get("camera_yaw"));
        row.floorHeight = parse_number<double>(get("floor_height"));
        row.floorNx = parse_number<double>(get("floor_nx"));
        row.floorNy = parse_number<double>(get("floor_ny"));
        row.floorNz = parse_number<double>(get("floor_nz"));
        row.wallNx = parse_number<double>(get("wall_nx"));
        row.wallNy = parse_number<double>(get("wall_ny"));
        row.wallNz = parse_number<double>(get("wall_nz"));
        rows.push_back(row);
    }
    return rows;
}

std::vector<std::uint8_t> read_binary(const fs::path &path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        throw std::runtime_error("cannot open movie: " + path.string());
    }
    return {std::istreambuf_iterator<char>(input), std::istreambuf_iterator<char>()};
}

std::uint32_t read_u32_le(const std::vector<std::uint8_t> &data, std::size_t offset) {
    if (offset + 4 > data.size()) {
        throw std::runtime_error("movie header is truncated");
    }
    return static_cast<std::uint32_t>(data[offset]) |
           (static_cast<std::uint32_t>(data[offset + 1]) << 8U) |
           (static_cast<std::uint32_t>(data[offset + 2]) << 16U) |
           (static_cast<std::uint32_t>(data[offset + 3]) << 24U);
}

std::vector<Input> movie_inputs(const std::vector<std::uint8_t> &data) {
    const auto count = read_u32_le(data, kM64SampleCountOffset);
    if (data.size() != kM64HeaderSize + static_cast<std::size_t>(count) * 4U) {
        throw std::runtime_error("unexpected .m64 size");
    }
    std::vector<Input> inputs(count);
    for (std::size_t sample = 0; sample < count; ++sample) {
        const auto offset = kM64HeaderSize + sample * 4U;
        inputs[sample].buttons = static_cast<std::uint16_t>(data[offset]) |
                                 (static_cast<std::uint16_t>(data[offset + 1]) << 8U);
        inputs[sample].x = static_cast<std::int8_t>(data[offset + 2]);
        inputs[sample].y = static_cast<std::int8_t>(data[offset + 3]);
    }
    return inputs;
}

double angle_to_radians(int angle) {
    return static_cast<double>(static_cast<std::int16_t>(angle)) * kPi / 32768.0;
}

PhysicsOutput air_physics(double forwardVel, int facingYaw, int cameraYaw, int rawX, int rawY) {
    double stickX = 0.0;
    double stickY = 0.0;
    if (rawX <= -8) stickX = rawX + 6.0;
    if (rawX >= 8) stickX = rawX - 6.0;
    if (rawY <= -8) stickY = rawY + 6.0;
    if (rawY >= 8) stickY = rawY - 6.0;
    double stickMag = std::hypot(stickX, stickY);
    if (stickMag > 64.0) {
        stickX *= 64.0 / stickMag;
        stickY *= 64.0 / stickMag;
        stickMag = 64.0;
    }
    const double intendedMag = stickMag * stickMag / 128.0;
    const double intendedYaw = std::atan2(-stickY, stickX) + angle_to_radians(cameraYaw);
    const double facing = angle_to_radians(facingYaw);
    const double dYaw = intendedYaw - facing;

    if (forwardVel < 0.0) forwardVel = std::min(0.0, forwardVel + 0.35);
    if (forwardVel > 0.0) forwardVel = std::max(0.0, forwardVel - 0.35);
    double sidewaysSpeed = 0.0;
    if (intendedMag > 0.0) {
        forwardVel += (intendedMag / 32.0) * std::cos(dYaw) * 1.5;
        sidewaysSpeed = (intendedMag / 32.0) * std::sin(dYaw) * 10.0;
    }
    if (forwardVel > 32.0) forwardVel -= 1.0;
    if (forwardVel < -16.0) forwardVel += 2.0;

    PhysicsOutput output;
    output.forwardVel = forwardVel;
    output.vx = forwardVel * std::sin(facing) + sidewaysSpeed * std::sin(facing + kPi / 2.0);
    output.vz = forwardVel * std::cos(facing) + sidewaysSpeed * std::cos(facing + kPi / 2.0);
    return output;
}

State initial_state(const Telemetry &row, const Input &input) {
    State state;
    state.forwardVel = row.forwardVel;
    state.verticalVel = row.verticalVel;
    state.x = row.x;
    state.y = row.y;
    state.z = row.z;
    state.lastX = input.x;
    state.lastY = input.y;
    return state;
}

State calibrated_step(const State &state, const Telemetry &current, const Telemetry &next,
                      const Input &referenceInput, int rawX, int rawY) {
    const auto candidatePhysics = air_physics(
        state.forwardVel, current.facingYaw, current.cameraYaw, rawX, rawY);
    const auto referencePhysics = air_physics(
        current.forwardVel, current.facingYaw, current.cameraYaw,
        referenceInput.x, referenceInput.y);

    State nextState = state;
    nextState.forwardVel = candidatePhysics.forwardVel + (next.forwardVel - referencePhysics.forwardVel);
    nextState.x += candidatePhysics.vx + ((next.x - current.x) - referencePhysics.vx);
    nextState.z += candidatePhysics.vz + ((next.z - current.z) - referencePhysics.vz);
    nextState.y += next.y - current.y;
    nextState.verticalVel += next.verticalVel - current.verticalVel;
    return nextState;
}

double horizontal_distance(const State &state, const Telemetry &target) {
    return std::hypot(state.x - target.x, state.z - target.z);
}

StateKey state_key(const State &state, const Telemetry &reference) {
    return {
        static_cast<int>(std::lround((state.x - reference.x) * 2.0)),
        static_cast<int>(std::lround((state.z - reference.z) * 2.0)),
        static_cast<int>(std::lround((state.forwardVel - reference.forwardVel) * 4.0)),
    };
}

void write_candidate(const fs::path &destination, const std::vector<std::uint8_t> &seedMovie,
                     const State &state, int startSample) {
    auto movie = seedMovie;
    for (int depth = 0; depth < state.depth; ++depth) {
        const auto sample = static_cast<std::size_t>(startSample + depth);
        const auto offset = kM64HeaderSize + sample * 4U;
        movie[offset + 2] = static_cast<std::uint8_t>(state.pathX[depth]);
        movie[offset + 3] = static_cast<std::uint8_t>(state.pathY[depth]);
    }
    std::ofstream output(destination, std::ios::binary);
    output.write(reinterpret_cast<const char *>(movie.data()), static_cast<std::streamsize>(movie.size()));
    if (!output) {
        throw std::runtime_error("failed to write candidate: " + destination.string());
    }
}

int main(int argc, char **argv) try {
    if (argc < 4 || argc > 10) {
        std::cerr << "usage: wkw_beam_sim SEED.m64 TELEMETRY.csv OUTPUT_DIR "
                     "[BEAM_WIDTH] [SHORTLIST] [START] [END] [GOAL] [TARGET]\n";
        return 2;
    }
    const fs::path moviePath = argv[1];
    const fs::path telemetryPath = argv[2];
    const fs::path outputDir = argv[3];
    const int beamWidth = argc >= 5 ? std::stoi(argv[4]) : 2500;
    const int shortlist = argc >= 6 ? std::stoi(argv[5]) : 20;
    const int startSample = argc >= 7 ? std::stoi(argv[6]) : 214;
    const int endSample = argc >= 8 ? std::stoi(argv[7]) : 221;
    const int goalSample = argc >= 9 ? std::stoi(argv[8]) : 222;
    const int targetSample = argc >= 10 ? std::stoi(argv[9]) : 224;
    if (beamWidth <= 0 || shortlist <= 0) {
        throw std::runtime_error("beam width and shortlist must be positive");
    }
    if (startSample > endSample || endSample >= goalSample || goalSample >= targetSample
        || endSample - startSample + 1 > kMaxDepth) {
        throw std::runtime_error("invalid search sample range");
    }

    const auto started = std::chrono::steady_clock::now();
    const auto movieData = read_binary(moviePath);
    const auto inputs = movie_inputs(movieData);
    const auto telemetryRows = read_telemetry(telemetryPath);
    std::unordered_map<int, Telemetry> telemetry;
    for (const auto &row : telemetryRows) telemetry[row.sample] = row;
    for (int sample = startSample; sample <= targetSample; ++sample) {
        if (!telemetry.contains(sample)) {
            throw std::runtime_error("telemetry is missing sample " + std::to_string(sample));
        }
    }
    if (inputs.size() <= static_cast<std::size_t>(targetSample)) {
        throw std::runtime_error("seed movie is too short");
    }

    std::vector<std::pair<int, int>> controls;
    for (int x = 88; x <= 120; x += 2) {
        for (int y = -128; y <= -96; y += 4) {
            controls.emplace_back(x, y);
        }
    }

    std::vector<State> beam = {initial_state(telemetry.at(startSample), inputs[startSample])};
    const auto &goalReference = telemetry.at(goalSample);
    const auto &target = telemetry.at(targetSample);
    const double desiredDx = target.x - goalReference.x;
    const double desiredDz = target.z - goalReference.z;
    const int branchCount = endSample - startSample + 1;

    for (int sample = startSample; sample <= endSample; ++sample) {
        const auto &current = telemetry.at(sample);
        const auto &next = telemetry.at(sample + 1);
        std::unordered_map<StateKey, State, StateKeyHash> distinct;
        distinct.reserve(static_cast<std::size_t>(beamWidth) * controls.size() / 2U);
        const double progress = static_cast<double>(sample - startSample + 1) / branchCount;
        for (const auto &state : beam) {
            for (const auto &[rawX, rawY] : controls) {
                State candidate = calibrated_step(state, current, next, inputs[sample], rawX, rawY);
                if (sample + 1 == 221) candidate.distance221 = horizontal_distance(candidate, target);
                if (sample + 1 == 222) candidate.distance222 = horizontal_distance(candidate, target);
                if (sample + 1 == 223) candidate.distance223 = horizontal_distance(candidate, target);
                const double changeX = rawX - state.lastX;
                const double changeY = rawY - state.lastY;
                candidate.smoothPenalty += 0.0005 * (changeX * changeX + changeY * changeY);
                candidate.lastX = rawX;
                candidate.lastY = rawY;
                candidate.pathX[candidate.depth] = static_cast<std::int8_t>(rawX);
                candidate.pathY[candidate.depth] = static_cast<std::int8_t>(rawY);
                candidate.depth++;
                const double actualDx = candidate.x - next.x;
                const double actualDz = candidate.z - next.z;
                const double errorX = actualDx - desiredDx * progress;
                const double errorZ = actualDz - desiredDz * progress;
                const double velocityDelta = candidate.forwardVel - next.forwardVel;
                candidate.guideScore = errorX * errorX + errorZ * errorZ
                                     + 0.04 * velocityDelta * velocityDelta
                                     + candidate.smoothPenalty;
                const auto key = state_key(candidate, next);
                auto found = distinct.find(key);
                if (found == distinct.end() || candidate.guideScore < found->second.guideScore) {
                    distinct[key] = candidate;
                }
            }
        }
        beam.clear();
        beam.reserve(distinct.size());
        for (auto &[key, state] : distinct) {
            (void) key;
            beam.push_back(std::move(state));
        }
        if (beam.size() > static_cast<std::size_t>(beamWidth)) {
            std::nth_element(beam.begin(), beam.begin() + beamWidth, beam.end(),
                             [](const State &a, const State &b) { return a.guideScore < b.guideScore; });
            beam.resize(beamWidth);
        }
        std::cout << "sample=" << sample << " states=" << beam.size() << " best_guide="
                  << std::min_element(beam.begin(), beam.end(),
                       [](const State &a, const State &b) { return a.guideScore < b.guideScore; })->guideScore
                  << '\n';
    }

    for (auto &state : beam) {
        for (int sample = endSample + 1; sample < targetSample; ++sample) {
            state = calibrated_step(state, telemetry.at(sample), telemetry.at(sample + 1),
                                    inputs[sample], inputs[sample].x, inputs[sample].y);
            if (sample + 1 == 221) state.distance221 = horizontal_distance(state, target);
            if (sample + 1 == 222) state.distance222 = horizontal_distance(state, target);
            if (sample + 1 == 223) state.distance223 = horizontal_distance(state, target);
        }
        state.finalScore = state.distance222 * state.distance222
                         + 0.10 * state.distance221 * state.distance221
                         + 0.20 * state.distance223 * state.distance223
                         + state.smoothPenalty;
    }
    std::sort(beam.begin(), beam.end(),
              [](const State &a, const State &b) { return a.finalScore < b.finalScore; });

    // The calibrated seed must reproduce the measured trajectory exactly.
    State replay = initial_state(telemetry.at(startSample), inputs[startSample]);
    double maxSeedError = 0.0;
    for (int sample = startSample; sample < targetSample; ++sample) {
        replay = calibrated_step(replay, telemetry.at(sample), telemetry.at(sample + 1),
                                 inputs[sample], inputs[sample].x, inputs[sample].y);
        const auto &reference = telemetry.at(sample + 1);
        maxSeedError = std::max({maxSeedError, std::abs(replay.x - reference.x),
                                 std::abs(replay.y - reference.y), std::abs(replay.z - reference.z),
                                 std::abs(replay.forwardVel - reference.forwardVel)});
    }
    if (maxSeedError > 1e-6) {
        throw std::runtime_error("calibrated seed drifted by " + std::to_string(maxSeedError));
    }

    fs::create_directories(outputDir);
    const fs::path statePath = moviePath.parent_path() / (moviePath.stem().string() + ".st");
    std::ofstream manifest(outputDir / "shortlist.csv");
    manifest << "rank,candidate,predicted_score,predicted_distance_221,predicted_distance_222,"
                "predicted_distance_223,edit_samples\n";
    const int emitted = std::min(shortlist, static_cast<int>(beam.size()));
    for (int rank = 0; rank < emitted; ++rank) {
        std::ostringstream name;
        name << "beam_" << std::setfill('0') << std::setw(3) << rank + 1 << ".m64";
        const fs::path destination = outputDir / name.str();
        write_candidate(destination, movieData, beam[rank], startSample);
        if (fs::exists(statePath)) {
            fs::copy_file(statePath, destination.parent_path() / (destination.stem().string() + ".st"),
                          fs::copy_options::overwrite_existing);
        }
        manifest << rank + 1 << ',' << name.str() << ',' << std::setprecision(12)
                 << beam[rank].finalScore << ',' << beam[rank].distance221 << ','
                 << beam[rank].distance222 << ',' << beam[rank].distance223 << ','
                 << beam[rank].depth << '\n';
    }
    const auto elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - started).count();
    std::cout << "controls=" << controls.size() << " beam_width=" << beamWidth
              << " shortlist=" << emitted << " calibrated_seed_max_error=" << maxSeedError
              << " elapsed_seconds=" << elapsed << " start_sample=" << startSample
              << " end_sample=" << endSample << " goal_sample=" << goalSample
              << " target_sample=" << targetSample << '\n';
    return 0;
} catch (const std::exception &error) {
    std::cerr << "wkw_beam_sim: " << error.what() << '\n';
    return 1;
}
