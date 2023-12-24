#include <iostream>
#include <vector>
#include <unordered_map>
#include <cmath>

// GLOBAL CONSTANTS
const double SUPPLY = 1e15;  // maximum supply of pool shares
const double FIRST = 1e8;   // amount of shares issued to first depositor

class InfinityPool {
public:
    InfinityPool(const std::vector<std::string>& tokens);

    std::unordered_map<std::string, double> status() const;

    void initialize(const std::unordered_map<std::string, double>& amount_in);

    double set_invariant();

    double calculate_spot_price(const std::string& asset, const std::string& currency) const;

    double deposit_all(const std::unordered_map<std::string, double>& amount_in);

    double deposit_one(const std::unordered_map<std::string, double>& amount_in);

    double deposit_any(const std::unordered_map<std::string, double>& amount_in);

    std::unordered_map<std::string, double> withdraw_all(double redeem);

    double withdraw_one(const std::string& token, double redeem);

    std::unordered_map<std::string, double> withdraw_any(double redeem, const std::unordered_map<std::string, double>& ratios);

    double swap(const std::string& t_in, const std::string& t_out, double amount_in);

    std::unordered_map<std::string, double> equalize(const std::unordered_map<std::string, double>& inputs, const std::unordered_map<std::string, double>& ratio_out);

private:
    std::vector<std::string> tokens;
    std::unordered_map<std::string, double> weights;
    std::unordered_map<std::string, double> balances;
    double shares_issued;
    double invariant;

    bool check_deposit_ratio(const std::unordered_map<std::string, double>& amount_in, double tolerance = 1e-9) const;
};

InfinityPool::InfinityPool(const std::vector<std::string>& tokens) {
    if (tokens.size() < 2) {
        throw std::invalid_argument("There must be at least two tokens in the pool.");
    }

    this->tokens = tokens;
    this->weights = {};
    this->balances = {};
    this->shares_issued = 0.0;
    this->invariant = 0.0;
}

std::unordered_map<std::string, double> InfinityPool::status() const {
    return {
        {"tokens", tokens},
        {"weights", weights},
        {"balances", balances},
        {"shares_supply", SUPPLY},
        {"shares_issued", shares_issued},
        {"invariant", invariant},
    };
}

void InfinityPool::initialize(const std::unordered_map<std::string, double>& amount_in) {
    if (amount_in.size() != tokens.size()) {
        throw std::invalid_argument("Keys of new balances must match the tokens in the pool.");
    }

    if (std::any_of(amount_in.begin(), amount_in.end(), [](const auto& balance) { return balance.second <= 0; })) {
        throw std::invalid_argument("Initial balances must be greater than zero.");
    }

    balances = amount_in;

    for (const auto& token : tokens) {
        weights[token] = amount_in.at(token) / std::accumulate(amount_in.begin(), amount_in.end(), 0.0,
                                                               [](double sum, const auto& balance) { return sum + balance.second; });
    }

    shares_issued = FIRST;
}

double InfinityPool::set_invariant() {
    invariant = 1.0;
    for (const auto& token : tokens) {
        invariant *= std::pow(balances[token], weights[token]);
    }
    return invariant;
}

double InfinityPool::calculate_spot_price(const std::string& asset, const std::string& currency) const {
    if (balances.find(asset) == balances.end() || balances.find(currency) == balances.end()) {
        throw std::invalid_argument("Invalid token indices.");
    }

    return (balances.at(asset) / weights.at(asset)) / (balances.at(currency) / weights.at(currency));
}

double InfinityPool::deposit_all(const std::unordered_map<std::string, double>& amount_in) {
    for (const auto& entry : amount_in) {
        if (entry.second <= 0) {
            throw std::invalid_argument("Amount in " + entry.first + " quantity " + std::to_string(entry.second) + " must be positive");
        }
    }

    if (weights.empty()) {
        if (!check_deposit_ratio(amount_in, 1e-6)) {
            throw std::invalid_argument("The deposit ratio does not match the existing token balances ratio.");
        }

        for (const auto& entry : amount_in) {
            balances[entry.first] += entry.second;
        }

        return (amount_in.at(tokens[0]) * SUPPLY) / balances.at(tokens[0]);
    } else {
        if (!check_deposit_ratio(amount_in, 1e-6)) {
            throw std::invalid_argument("The deposit ratio does not match the existing token balances ratio.");
        }

        for (const auto& entry : amount_in) {
            balances[entry.first] += entry.second;
        }

        set_invariant();
        return (amount_in.at(tokens[0]) * SUPPLY) / balances.at(tokens[0]);
    }
}

bool InfinityPool::check_deposit_ratio(const std::unordered_map<std::string, double>& amount_in, double tolerance) const {
    std::vector<double> existing_ratio;
    std::transform(balances.begin(), balances.end(), std::back_inserter(existing_ratio),
                   [this](const auto& entry) { return entry.second / std::accumulate(balances.begin(), balances.end(), 0.0,
                                                                                        [](double sum, const auto& balance) { return sum + balance.second; }); });

    std::vector<double> deposit_ratio;
    std::transform(amount_in.begin(), amount_in.end(), std::back_inserter(deposit_ratio),
                   [this](const auto& entry) { return entry.second / std::accumulate(amount_in.begin(), amount_in.end(), 0.0,
                                                                                      [](double sum, const auto& balance) { return sum + balance.second; }); });

    return std::equal(existing_ratio.begin(), existing_ratio.end(), deposit_ratio.begin(),
                      [tolerance](double a, double b) { return std::abs(a - b) < tolerance; });
}

double InfinityPool::deposit_one(const std::unordered_map<std::string, double>& amount_in) {
    if (weights.empty()) {
        throw std::invalid_argument("Single-asset deposit is not allowed until weights are assigned.");
    }

    if (std::count_if(amount_in.begin(), amount_in.end(), [](const auto& entry) { return entry.second != 0; }) != 1) {
        throw std::invalid_argument("Exactly one element in amount_in should be non-zero.");
    }

    std::string t_key = std::find_if(amount_in.begin(), amount_in.end(), [](const auto& entry) { return entry.second != 0; })->first;

    if (amount_in.at(t_key) < 0) {
        throw std::invalid_argument("The deposited amount must be positive");
    }

    double shares_to_issue = (amount_in.at(t_key) * SUPPLY) / balances.at(t_key);
    balances.at(t_key) += amount_in.at(t_key);

    set_invariant();
    return shares_to_issue;
}

double InfinityPool::deposit_any(const std::unordered_map<std::string, double>& amount_in) {
    if (weights.empty()) {
        throw std::invalid_argument("Multi-asset deposit is not allowed until weights are assigned.");
    }

    if (!check_deposit_ratio(amount_in, 1e-6)) {
        throw std::invalid_argument("The deposit ratio does not match the existing token balances ratio.");
    }

    for (const auto& entry : amount_in) {
        balances[entry.first] += entry.second;
    }

    set_invariant();
    return (amount_in.at(tokens[0]) * SUPPLY) / balances.at(tokens[0]);
}

std::unordered_map<std::string, double> InfinityPool::withdraw_all(double redeem) {
    if (redeem <= 0) {
        throw std::invalid_argument("Redeem amount must be positive.");
    }

    double redeem_ratio = redeem / SUPPLY;
    if (redeem_ratio > shares_issued) {
        throw std::invalid_argument("Redeem amount exceeds the total shares issued.");
    }

    std::unordered_map<std::string, double> amount_out;
    for (const auto& token : tokens) {
        amount_out[token] = balances[token] * (1.0 - std::pow(shares_issued - redeem_ratio, 1.0 / weights[token]));
        balances[token] -= amount_out[token];
    }

    shares_issued -= redeem_ratio;
    set_invariant();
    return amount_out;
}

double InfinityPool::withdraw_one(const std::string& token, double redeem) {
    if (weights.empty()) {
        throw std::invalid_argument("Single-asset withdrawal is not allowed until weights are assigned.");
    }

    if (redeem <= 0) {
        throw std::invalid_argument("Redeem amount must be positive.");
    }

    double redeem_ratio = redeem / SUPPLY;
    if (redeem_ratio > shares_issued) {
        throw std::invalid_argument("Redeem amount exceeds the total shares issued.");
    }

    double amount_out = balances[token] * (1.0 - std::pow(shares_issued - redeem_ratio, 1.0 / weights[token]));
    balances[token] -= amount_out;

    shares_issued -= redeem_ratio;
    set_invariant();
    return amount_out;
}

std::unordered_map<std::string, double> InfinityPool::withdraw_any(double redeem, const std::unordered_map<std::string, double>& ratios) {
    if (weights.empty()) {
        throw std::invalid_argument("Multi-asset withdrawal is not allowed until weights are assigned.");
    }

    if (!check_deposit_ratio(ratios, 1e-6)) {
        throw std::invalid_argument("The withdrawal ratio does not match the existing token balances ratio.");
    }

    if (redeem <= 0) {
        throw std::invalid_argument("Redeem amount must be positive.");
    }

    double redeem_ratio = redeem / SUPPLY;
    if (redeem_ratio > shares_issued) {
        throw std::invalid_argument("Redeem amount exceeds the total shares issued.");
    }

    std::unordered_map<std::string, double> amount_out;
    for (const auto& token : tokens) {
        amount_out[token] = ratios.at(token) * redeem_ratio;
        balances[token] -= amount_out[token];
    }

    shares_issued -= redeem_ratio;
    set_invariant();
    return amount_out;
}

double InfinityPool::swap(const std::string& t_in, const std::string& t_out, double amount_in) {
    if (weights.empty()) {
        throw std::invalid_argument("Swapping is not allowed until weights are assigned.");
    }

    if (amount_in <= 0) {
        throw std::invalid_argument("Amount in must be positive.");
    }

    if (balances[t_in] < amount_in) {
        throw std::invalid_argument("Insufficient balance for the input token.");
    }

    double amount_out = balances[t_out] * (1.0 - std::pow((balances[t_in] - amount_in) / balances[t_in], weights[t_in] / weights[t_out]));
    balances[t_in] -= amount_in;
    balances[t_out] += amount_out;

    set_invariant();
    return amount_out;
}

std::unordered_map<std::string, double> InfinityPool::equalize(const std::unordered_map<std::string, double>& inputs, const std::unordered_map<std::string, double>& ratio_out) {
    if (weights.empty()) {
        throw std::invalid_argument("Equalizing is not allowed until weights are assigned.");
    }

    if (!check_deposit_ratio(inputs, 1e-6) || !check_deposit_ratio(ratio_out, 1e-6)) {
        throw std::invalid_argument("The input or output ratio does not match the existing token balances ratio.");
    }

    double total_weight_in = std::accumulate(weights.begin(), weights.end(), 0.0,
        [this, &inputs](double acc, const auto& weight_entry) { return acc + weight_entry.second * inputs.at(weight_entry.first); });

    std::unordered_map<std::string, double> amount_out;
    for (const auto& token : tokens) {
        amount_out[token] = balances[token] * (std::pow(total_weight_in / weights[token], 1.0 / weights[token]) - 1.0);
        balances[token] += inputs.at(token);
    }

    set_invariant();
    return amount_out;
}

int main() {
    std::vector<std::string> tokens = {"X", "Y", "Z"};
    InfinityPool pool(tokens);

    // Example usage similar to the Python code...

    return 0;
}
