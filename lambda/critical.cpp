#include <algorithm>
#include <chrono>
#include <iostream>
#include <ostream>
#include <string>
#include <sys/stat.h>
#include <thread>
#include <vector>
#include <sstream>
#include <memory>

enum class TermType {VAR,
               LAM,
               APP
              };

class LambdaTerm {
public:

    //regist
    TermType type;
    int var_index = -1;

    std::unique_ptr<LambdaTerm> lam_term;
    std::unique_ptr<LambdaTerm> left_term;
    std::unique_ptr<LambdaTerm> right_term;

    LambdaTerm() = default;

    static std::unique_ptr<LambdaTerm> Var(int index);
    static std::unique_ptr<LambdaTerm> Lam(std::unique_ptr<LambdaTerm> body );
    static std::unique_ptr<LambdaTerm> App(std::unique_ptr<LambdaTerm> left,
                                           std::unique_ptr<LambdaTerm> right);

        // call print
    void print(std::ostream& os) const;
    void print(std::ostream& os, std::vector<std::string>& context) const;
};

std::unique_ptr<LambdaTerm> LambdaTerm::Var(int index) {
    auto term = std::make_unique<LambdaTerm>();
    term -> type      = TermType::VAR;
    term -> var_index = index;
    return term;
}

std::unique_ptr<LambdaTerm> LambdaTerm::Lam(std::unique_ptr<LambdaTerm> body) {
    auto term = std::make_unique<LambdaTerm>();
    term -> type     = TermType::LAM;
    term -> lam_term = std::move(body);
    return term;
}

std::unique_ptr<LambdaTerm> LambdaTerm::App(std::unique_ptr<LambdaTerm> left, std::unique_ptr<LambdaTerm> right) {
    auto term = std::make_unique<LambdaTerm>();
    term -> type       = TermType::APP;
    term -> left_term  = std::move(left );
    term -> right_term = std::move(right);
    return term;
}

std::string chooseVarName(int index) {
    static const std::vector<std::string> base_names = {
        "x", "y", "z", "a", "b", "c", "d", "e", "f",
        "g", "h", "i", "j", "k", "l", "m", "n", "o",
        "p", "q", "r", "s", "t", "u", "v"
    };

    int base_size = base_names.size();
    int round = index / base_size;
    int which = index % base_size;

    std::string name = base_names[which];
    if (round == 0)
        return name;
    else
        return name + std::to_string(round);
}

void LambdaTerm::print(std::ostream& os, std::vector<std::string>& context) const {
    switch (type) {
        case TermType::VAR:
            if (var_index < context.size())
                os << context[context.size() - 1 - var_index];
            else
                os << "?" << var_index;
            break;

        case TermType::LAM: {
            std::string var_name = chooseVarName(context.size());
            context.push_back(var_name);
            os << "(lambda " << var_name << ". ";
            if (lam_term) lam_term->print(os, context);
            os << ")";
            context.pop_back();
            break;
        }

        case TermType::APP:
            os << "(";
            if (left_term)  left_term  -> print(os, context);
            os << " ";
            if (right_term) right_term -> print(os, context);
            os << ")";
            break;
    }
}


// wrapper @print
void LambdaTerm::print(std::ostream& os) const {
    std::vector<std::string> context;
    print(os, context);
}

// recollect parser
enum class TokenType {
    LPAREN,
    RPAREN,

    LAMBDA,
    DOT,
    IDENT
};

struct Token {
    TokenType type;
    std::string text;
};

std::vector<Token> tokenise(const std::string& input);

class Parser {
public:
    Parser(const std::vector<Token>& tokens): tokens(tokens), pos(0) {}

    std::unique_ptr<LambdaTerm> parseTerm();

private:
    const std::vector<Token>& tokens;
    size_t pos;
    std::vector<std::string> context;

    std::unique_ptr<LambdaTerm> parseAtom();
    std::string expectIdent();
    void expect(TokenType type);
    bool match (TokenType type);
};

std::unique_ptr<LambdaTerm> Parser::parseAtom() {
    if (match(TokenType::LPAREN)) {
        if (match(TokenType::LAMBDA)) {
            std::string var = expectIdent();
            expect(TokenType::DOT);
            context.push_back(var);
            auto body = parseTerm();
            expect(TokenType::RPAREN);
            context.pop_back();
            return LambdaTerm::Lam(std::move(body));
        } else {
            auto inner = parseTerm();
            expect(TokenType::RPAREN);
            return inner;
        }
    } else if (tokens[pos].type == TokenType::IDENT) {
        std::string name = tokens[pos++].text;
        for (int i = context.size() - 1; i >= 0; --i) {
            if (context[i] == name) {
                return LambdaTerm::Var(context.size() - 1 - i);
            }
        }
        throw std::runtime_error("Unbound variable: " + name);
    }
    throw std::runtime_error("Unexpected token.");
}

// term = iter (atom) := atom { atom }
std::unique_ptr<LambdaTerm> Parser::parseTerm() {
    auto left = parseAtom();
    while (pos < tokens.size() && tokens[pos].type != TokenType::RPAREN) {
        auto right = parseAtom();
        left = LambdaTerm::App(std::move(left), std::move(right));
    }
    return left;
}

std::vector<Token> tokenise(const std::string& input) {
    std::vector<Token> tokens;
    size_t i = 0;

    while (i < input.length()) {
        char ch = input[i];

        if (isspace(ch)) {
            ++i;
            continue;
        }

        if (ch == '(') {
            tokens.push_back({TokenType::LPAREN, "("});
            ++i;
        } else if (ch == ')') {
            tokens.push_back({TokenType::RPAREN, ")"});
            ++i;
        } else if (ch == '.') {
            tokens.push_back({TokenType::DOT,    "."});
            ++i;
        } else if (std::isalpha(ch)) {
            std::string word;
            while (i < input.length() && (std::isalnum(input[i]) || input[i] == '_')) {
                word += input[i++];
            }
            if (word == "lambda") {
                tokens.push_back({TokenType::LAMBDA, word});
            } else {
                tokens.push_back({TokenType::IDENT,  word});
            }
        } else {
            throw std::runtime_error(std::string("Unexpected character: ") + ch + std::string("."));
        }
    }

    return tokens;
}

bool Parser::match(TokenType type) {
    if (pos < tokens.size() && tokens[pos].type == type) {
        ++pos;
        return true;
    }
    return false;
}

void Parser::expect(TokenType type) {
    if (!match(type)) {
        throw std::runtime_error("Expected different token type.");
    }
}

std::string Parser::expectIdent() {
    if (pos < tokens.size() && tokens[pos].type == TokenType::IDENT) {
        return tokens[pos++].text;
    }
    throw std::runtime_error("Expected identifier.");
}

int findFreshVarIndex(const LambdaTerm* term, int used_index) {
    if (!term) return used_index;

    switch (term -> type) {
        case TermType::VAR:
            return (term -> var_index == used_index)
                    ? used_index + 1
                    : std::max(used_index, term -> var_index + 1);

        case TermType::LAM:
            return findFreshVarIndex(term -> lam_term.get(), used_index);

        case TermType::APP: {
            int left  = findFreshVarIndex(term ->  left_term.get(), used_index);
            int right = findFreshVarIndex(term -> right_term.get(), used_index);
            return std::max(left, right);
        }
    }

    return used_index;
}

std::unique_ptr<LambdaTerm> Clone(const LambdaTerm* term) {
    if (!term) return nullptr;

    switch (term -> type) {
        case TermType::VAR:
            return LambdaTerm::Var(term -> var_index);

        case TermType::LAM:
            return LambdaTerm::Lam(Clone(term -> lam_term.get()));

        case TermType::APP:
            return LambdaTerm::App(
                 Clone(term ->  left_term.get()),
                Clone(term -> right_term.get())
            );
    }

    return nullptr;
}

std::unique_ptr<LambdaTerm> substitute(const LambdaTerm* term, int var_index, const LambdaTerm* arg_term) {
    if (!term) return nullptr;

    switch (term->type) {
        case TermType::VAR:
            if (term->var_index == var_index)
                return Clone(arg_term);
            else
                return LambdaTerm::Var(term->var_index);

        case TermType::LAM: {
            auto new_body = substitute(term -> lam_term.get(), var_index + 1, arg_term);
            return LambdaTerm::Lam(std::move(new_body));
        }

        case TermType::APP: {
            auto left  = substitute(term ->  left_term.get(), var_index, arg_term);
            auto right = substitute(term -> right_term.get(), var_index, arg_term);
            return LambdaTerm::App(std::move(left), std::move(right));
        }
    }
    return nullptr;
}

std::unique_ptr<LambdaTerm> evaluate(const LambdaTerm* term) {
    if (!term) return nullptr;

    switch (term -> type) {
        case TermType::VAR:
            return LambdaTerm::Var(term->var_index);

        case TermType::LAM: {
            auto new_body = evaluate(term->lam_term.get());
            return LambdaTerm::Lam(std::move(new_body));
        }

        case TermType::APP: {
            auto left_eval = evaluate(term->left_term.get());

            if (left_eval -> type == TermType::LAM) {
                const auto* body = left_eval->lam_term.get();
                auto substituted = substitute(body, 0, term->right_term.get());
                return evaluate(substituted.get());
            } else {
                auto right_eval = evaluate(term->right_term.get());
                return LambdaTerm::App(std::move(left_eval), std::move(right_eval));
            }
        }
    }

    return nullptr;
}

std::string toString(const LambdaTerm* term) {
    std::ostringstream oss;
    if (term) term -> print(oss);
    return oss.str();
}

struct Point {
    int x;
    int y;
};

struct Dimension {
    int width;
    int height;
};


Dimension getTermBoundingBox(const LambdaTerm* term) {
    if (!term) return {0, 0};

    switch (term->type) {
        case TermType::VAR:
            return {2, 1};

        case TermType::LAM: {
            Dimension inner = getTermBoundingBox(term->lam_term.get());
            return {inner.width + 8, std::max(2, inner.height + 1)};
        }

        case TermType::APP: {
            Dimension left  = getTermBoundingBox(term->left_term.get());
            Dimension right = getTermBoundingBox(term->right_term.get());
            return {left.width + right.width + 2, std::max(left.height, right.height) + 1};
        }
    }
    return {0, 0};
}

void drawLine(std::ostream& os, Point p1, Point p2) {
    os << "drawLine " << p1.x << " " << p1.y << " " << p2.x << " " << p2.y << '\n';
}

void drawLineV(std::ostream& os, Point p1, Point p2) {
    os << "drawLineV " << p1.x << " " << p1.y << " " << p2.x << " " << p2.y << '\n';
}

void drawText(std::ostream& os, const std::string& text, Point p) {
    os << "drawText " << p.x << " " << p.y << " " << text << '\n';
}

void drawTerm(std::ostream& os, const LambdaTerm* term, Point origin, std::vector<std::string> context = {}) {
    if (!term) return;

    Dimension dim = getTermBoundingBox(term);

    switch (term->type) {
        case TermType::VAR: {
            std::string name = (term->var_index < context.size())
                             ? context[context.size() - 1 - term->var_index]
                             : "?" + std::to_string(term->var_index);
            drawText(os, name, origin);
            break;
        }

        case TermType::LAM: {
            std::string var_name = chooseVarName(context.size());
            context.push_back(var_name);

            drawText(os, "(lambda " + var_name + ".", origin);

            Point inner_origin = {origin.x + 4, origin.y};
            drawTerm(os, term->lam_term.get(), inner_origin, context);

            drawText(os, ")", {origin.x + dim.width - 4, origin.y});
            drawLine(os, {origin.x + 2, origin.y}, {origin.x + 2, origin.y + dim.height});

            context.pop_back();
            break;
        }

        case TermType::APP: {
            Dimension left_dim = getTermBoundingBox(term->left_term.get());

            Point left_origin = origin;
            Point right_origin = {origin.x + left_dim.width + 2, origin.y};

            drawTerm(os, term->left_term.get(),  left_origin,  context);
            drawTerm(os, term->right_term.get(), right_origin, context);

            drawLineV(os,
                      {origin.x + dim.width / 2, origin.y + 1},
                      {origin.x + dim.width / 2, origin.y + dim.height});
            break;
        }
    }
}

std::string generateAnimationFrame(const LambdaTerm* term, int frame_num) {
    std::stringstream ss;
    drawTerm(ss, term, {frame_num * 50, 20});
    return ss.str();
}

std::vector<std::string> generateAnimationFrames(const LambdaTerm* term) {
    std::vector<std::string> frames;
    for (int i = 0; i < 10; ++i) {
        frames.push_back(generateAnimationFrame(term, i));
    }
    return frames;
}



int main() {
    std::string term_str;
    std::cout << "Enter a lambda calculus term: ";
    std::getline(std::cin, term_str);

    try {
        std::vector<Token> tokens = tokenise(term_str);
        Parser parser(tokens);
        std::unique_ptr<LambdaTerm> term = parser.parseTerm();

        std::cout << "Original term: ";
        term -> print(std::cout);
        std::cout << std::endl;

        std::unique_ptr<LambdaTerm> evaluated_term = evaluate(term.get());

        if (evaluated_term) {
            std::cout << "Generating animation for evaluated term...\n";
            std::vector<std::string> frames = generateAnimationFrames(evaluated_term.get());

            for (const std::string& frame : frames) {
                std::cout << frame << std::endl;
                std::this_thread::sleep_for(std::chrono::milliseconds(500));
            }

            std::cout << "Evaluated term: ";
            evaluated_term -> print(std::cout);
            std::cout << std::endl;
        } else {
            std::cout << "Error: Evaluation failed." << std::endl;
        }

    } catch (const std::exception& ex) {
        std::cerr << "Error while parsing or evaluating: " << ex.what() << std::endl;
        return 1;
    }

    return 0;
}
