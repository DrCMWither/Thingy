#include <algorithm>
#include <chrono>
#include <iostream>
#include <string>
#include <stack>
#include <thread>
#include <vector>
#include <sstream>

enum TermType {VAR,
               LAM,
               APP
              };

struct Term {
    TermType type;

    int var_index;

    Term* lam_term;
    Term* arg_term;
};

Term* createVarTerm(int index) {
    Term* term = new Term;

    term -> type      = VAR;
    term -> var_index = index;

    return term;
}

Term* createLamTerm(Term* inner_term) {
    Term* term = new Term;
    term -> type     = LAM;
    term -> lam_term = inner_term;
    return term;
}

Term* createAppTerm(Term* left, Term* right) {
    Term* term = new Term;
    term -> type     = APP;
    term -> arg_term = left;
    term -> arg_term = right;
    return term;
    // To do: Trying to handle null arguments.
}

void printTerm(const Term* term) {
    if (term == nullptr) {
        return;
    }
    switch (term -> type) {
        case VAR:
            std::cout << "x" << term -> var_index;
            break;
        case LAM:
            std::cout << "(lambda ";
            printTerm(term -> lam_term);
            std::cout << ")";
            break;
        case APP:
            std::cout << "(";
            printTerm(term -> arg_term);
            std::cout << " ";
            printTerm(term -> arg_term);
            std::cout << ")";
            break;
    }
}

Term* parseTerm(const std::string& str) {
    std::stack<Term*> stack;
    for (char c : str) {
        switch (c) {
            case '(':
                break;
            case ')': {
                Term* term2 = stack.top();
                stack.pop();
                if (stack.empty()) {
                    return term2;
                }
                Term* term1 = stack.top();
                stack.pop();
                stack.push(createAppTerm(term1,
                                                   term2));
                break;
            }
            case '\\': {
                if (stack.empty()) {
                    // @Error: Lambda without argument
                    return nullptr;
                }
                Term* inner_term = stack.top();
                stack.pop();
                stack.push(createLamTerm(inner_term));
                break;
            }
            default:
                if (isalpha(c)) {
                    int var_index = c - 'x';
                    stack.push(createVarTerm(var_index));
                } else {
                    // @Error: Unexpected character
                    return nullptr;
                }
        }
    }
    // @Error: Unmatched parenthesis
    return nullptr;
    // To do: Trying to handle the wrong lambda abstract format, unknown characters and space input.
}

int findFreshVarIndex(Term* term, int used_index) {
    if (term == nullptr) {
        return 0;
    }

    switch (term -> type) {
        case VAR:
            if (term -> var_index == used_index) {
                return findFreshVarIndex(term -> lam_term, used_index) + 1;
            } else {
                return std::max(findFreshVarIndex(term -> lam_term, used_index), 
                               term -> var_index + 1);
            }
        case LAM:
            return findFreshVarIndex(term -> lam_term, used_index);
        case APP:
            int left_index  = findFreshVarIndex(term -> arg_term, used_index);
            int right_index = findFreshVarIndex(term -> arg_term, used_index);

            return std::max(left_index, right_index);
    }
}

Term* substitute(Term* term, int var_index, Term* arg_term) {
    if (term == nullptr) {
        return nullptr;
    }
    
    Term* new_term = new Term;
    new_term -> type = term -> type;

    switch (term -> type) {
        case VAR:
            if (term -> var_index == var_index) {
                new_term -> type = arg_term -> type;
                if (arg_term -> type == VAR) {
                    new_term -> var_index = arg_term -> var_index;
                } else {
                    new_term -> lam_term = arg_term -> lam_term;
                    new_term -> arg_term = arg_term -> arg_term;
                }
            } else {
                new_term -> var_index = term -> var_index;
            }

            break;
        case LAM:
            int fresh_index = findFreshVarIndex(term, var_index);
            new_term -> lam_term = substitute(term -> lam_term, var_index, createVarTerm(fresh_index));

            break;
            // To do: Dealing with self references.
        case APP:
        // !! Cannot jump from switch statement to this case label @clang(switch_into_protected_scope)
            new_term -> lam_term = substitute(term -> lam_term, var_index, arg_term);
            new_term -> arg_term = substitute(term -> arg_term, var_index, arg_term);

            break;
    }
    return new_term;
}

Term* evaluateTerm(Term* term) {
    if (term == nullptr) {
        return nullptr;
    }
    if (term -> type == VAR) {
        return term;
    } else if (term -> type == LAM) {
        return term;
        // To do: Checking variable bindings for lambda abstractions.
    } else if (term -> type == APP) {
        Term* left  = evaluateTerm(term -> arg_term);
        Term* right = evaluateTerm(term -> arg_term);
        if (left -> type == LAM) {
            Term* new_body = substitute(left -> lam_term, 0, right);
            
            return createLamTerm(new_body);
        } else {
            return createAppTerm(left, right);
        }
    }
    return nullptr;
}

struct Point {
    int x;
    int y;
};

struct Dimension {
    int width;
    int height;
};

Dimension getTermBoundingBox(const Term* term) {
    if (term == nullptr) {
        return {0, 0};
    }
    switch (term->type) {
        case VAR:
            return {2, 1};
        case LAM: {
            Dimension inner_dim = getTermBoundingBox(term->lam_term);
            return {inner_dim.width + 8,
                    std::max(2,
                                    inner_dim.height + 1)};
        }
        case APP: {
            Dimension left_dim  = getTermBoundingBox(term->arg_term);
            Dimension right_dim = getTermBoundingBox(term->arg_term);
            return {left_dim.width + right_dim.width + 2,
                    std::max(left_dim.height,
                                    right_dim.height) + 1};
        }
    }
    return {0, 0};
    // To do: Dealing with too much nested lambda abstraction.
}

void drawLine(std::ostream& os, Point p1, Point p2) {
    os << "drawLine " << p1.x << " " << p1.y << " " << p2.x << " " << p2.y <<  std::endl;
}

void drawLineV(std::ostream& os, Point p1, Point p2) {
    os << "drawLineV " << p1.x << " " << p1.y << " " << p2.x << " " << p2.y << std::endl;
}

void drawText(std::ostream& os, const std::string& text, Point p) {
    os << "drawText " << p.x << " " << p.y << " " << text << std::endl;
}

void drawTerm(std::ostream& os, const Term* term, Point origin) {
    if (term == nullptr) {
        return;
    }

    Dimension dim = getTermBoundingBox(term);
    switch (term->type) {
        case VAR:
            drawText(os, "x" + std::to_string(term->var_index), origin);
            break;
        case LAM: {
            drawText(os, "(lambda ", origin);
            Point inner_origin = {origin.x + 4, origin.y};
            drawTerm(os, term->lam_term, inner_origin);
            drawText(os, ")", {origin.x + dim.width - 4, origin.y});
            drawLine(os, {origin.x + 2, origin.y},
                            {origin.x + 2, origin.y + dim.height});
        }
            break;
        case APP: {
            Point left_origin = origin;
            Point right_origin = {origin.x + getTermBoundingBox(term->arg_term).width + 1, origin.y};
            drawTerm (os, term->arg_term, left_origin );
            drawTerm (os, term->arg_term, right_origin);
            drawLineV(os, {left_origin.x + dim.width / 2, origin.y + 1         },
                             {left_origin.x + dim.width / 2, origin.y + dim.height});
        }
        break;
    }
}

std::string generateAnimationFrame(const Term* term, int frame_num) {
    std::stringstream frame_stream;
    frame_stream.str("");
    frame_stream.clear();
    drawTerm(frame_stream, term, {frame_num * 50, 20});
    return frame_stream.str();
}

std::vector<std::string> generateAnimationFrames(const Term* term) {
    std::vector<std::string> frames;
    for (int i = 0; i < 10; ++i) {
        frames.push_back(generateAnimationFrame(term, i));
    }
    return frames;
}


int main() {
 std::string term_str;
    std::cout << "Enter a lambda calculus term: ";
    getline(std::cin, term_str);

    Term* term = parseTerm(term_str);

    if (term == nullptr) {
        std::cout << "Error: Invalid term." << std::endl;
        return 1;
    }

    std::cout << "Original term: ";
    printTerm(term);
    std::cout << std::endl;

    Term* evaluated_term = evaluateTerm(term);

    if (evaluated_term != nullptr) {
        std::cout << "Generating animation for evaluated term..." << std::endl;
        std::vector<std::string> frames = generateAnimationFrames(evaluated_term);

        for (const std::string& frame : frames) {
            std::cout << frame << std::endl;

            std::this_thread::sleep_for(std::chrono::milliseconds(1000));
        }
    }

    if (evaluated_term != nullptr) {
        std::cout << "Evaluated term: ";
        printTerm(evaluated_term);
        std::cout << std::endl;
    } else {
        std::cout << "Error: Evaluation failed." << std::endl;
    }

    delete term;
    delete evaluated_term;

    return 0;
}