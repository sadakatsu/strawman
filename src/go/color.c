#include "color.h"

bool is_liberty(Color color) {
    return color == Empty;
}

inline Color inverse(Color color) {
    Color result;
    switch (color) {
        case Empty: result = Empty; break;
        case Black: result = White; break;
        case White: result = Black; break;
        default: result = -1; // THIS IS AN ERROR!
    }
    return result;
}
