#ifndef GO_COORDINATE_H
#define GO_COORDINATE_H

#include <stddef.h>
#include "constants.h"

struct _coord;
typedef struct _coord Coordinate;
struct _coord {
    size_t span;
    size_t row;
    size_t column;
    size_t index;
    size_t neighbor_count;
    size_t corner_count;
    Coordinate *neighbors[4];
    Coordinate *corners[4];
};



struct _coords;
typedef struct _coords Coordinates;
struct _coords {
    size_t span;
    size_t count;
    Coordinate coordinates[MAX_SPAN * MAX_SPAN];
};

Coordinates *get_coordinates(size_t span);

#endif //GO_COORDINATE_H
