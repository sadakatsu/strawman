#include <stdbool.h>
#include <string.h>
#include "coordinate.h"

static bool initialized = false;
static Coordinates cache[MAX_SPAN] = {};

Coordinates *get_coordinates(size_t span) {
    // Zero out all the arrays in the cache if this is the first call.
    if (!initialized) {
        memset(cache, 0, sizeof cache);
        initialized = true;
    }

    // Return NULL if the requested size is invalid.
    if (span < 1 || span > MAX_SPAN) {
        return NULL;
    }

    // Populate the requested size if it has not been populated before.
    Coordinates *coordinates = &(cache[span - 1]);
    if (coordinates->span != span) {
        // Set the core fields.
        const size_t area = span * span;
        coordinates->span = span;
        coordinates->count = area;

        // Set all the basic data for each Coordinate.
        for (size_t i = 0; i < area; ++i) {
            Coordinate *coordinate = &(coordinates->coordinates[i]);
            coordinate->span = span;
            coordinate->index = i;
            coordinate->row = i / span + 1;
            coordinate->column = i % span + 1;
            coordinate->neighbor_count = 0;
            coordinate->corner_count = 0;
            memset(&(coordinate->neighbors), 0, 4 * sizeof(Coordinate *));
            memset(&(coordinate->corners), 0, 4 * sizeof(Coordinate *));
        }

        // Now that all the Coordinates are prepared, fill in their neighbor and corner arrays.
        for (size_t row = 1, i = 0; row <= span; ++row) {
            for (size_t column = 1; column <= span; ++i, ++column) {
                Coordinate *coordinate = &(coordinates->coordinates[i]);

                bool has_bottom = row + 1 <= span;
                if (column + 1 <= span) {
                    Coordinate *neighbor = &(coordinates->coordinates[i + 1]);
                    coordinate->neighbors[coordinate->neighbor_count++] = neighbor;
                    neighbor->neighbors[neighbor->neighbor_count++] = coordinate;

                    if (row > 1) {
                        Coordinate *corner = &(coordinates->coordinates[i - span + 1]);
                        coordinate->corners[coordinate->corner_count++] = corner;
                        corner->corners[corner->corner_count++] = coordinate;
                    }

                    if (has_bottom) {
                        Coordinate *corner = &(coordinates->coordinates[i + span + 1]);
                        coordinate->corners[coordinate->corner_count++] = corner;
                        corner->corners[corner->corner_count++] = coordinate;
                    }
                }
                if (has_bottom) {
                    Coordinate *neighbor = &(coordinates->coordinates[i + span]);
                    coordinate->neighbors[coordinate->neighbor_count++] = neighbor;
                    neighbor->neighbors[neighbor->neighbor_count++] = coordinate;
                }
            }
        }
    }

    // Return the requested Coordinates.
    return coordinates;
}
