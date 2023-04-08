#version 430

layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;

uniform int size;
uniform sampler3D inputTexture;
layout(rgba32f) uniform image3D outputTexture;

int countNeighbors(ivec3 coord) {
    int count = 0;

    for (int dx = -1; dx <= 1; ++dx) {
        for (int dy = -1; dy <= 1; ++dy) {
            for (int dz = -1; dz <= 1; ++dz) {
                if (dx == 0 && dy == 0 && dz == 0) continue;

                ivec3 neighbor = ivec3(coord.x + dx, coord.y + dy, coord.z + dz);

                // clamp neighbor coordinates within grid boundaries
                neighbor = clamp(neighbor, ivec3(0), ivec3(size - 1));

                count += int(texelFetch(inputTexture, neighbor, 0).r > 0.5);
            }
        }
    }

    return count;
}

void main() {
    ivec3 coord = ivec3(gl_GlobalInvocationID.xyz);

    float isAlive = texelFetch(inputTexture, coord, 0).r;
    int neighbors = countNeighbors(coord);

    if (isAlive > 0.5) {
        if (neighbors == 2 || neighbors == 3)
            imageStore(outputTexture, coord, vec4(1, 0, 0, 1));
        else
            imageStore(outputTexture, coord, vec4(0, 0, 0, 1));
    } else {
        if (neighbors == 3)
            imageStore(outputTexture, coord, vec4(1, 0, 0, 1));
        else
            imageStore(outputTexture, coord, vec4(0, 0, 0, 1));
    }
}