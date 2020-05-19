#ifndef GO_COLOR_H
#define GO_COLOR_H

#include <stdbool.h>

typedef enum { Empty, Black, White } Color;

bool is_liberty(Color color);
Color inverse(Color color);

#endif //GO_COLOR_H
