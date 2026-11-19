#version 330 core

layout(points) in;
layout(triangle_strip, max_vertices = 4) out;

uniform mat4x4 viewM;
uniform mat4x4 projectionM;
uniform vec2 size;

out vec2 texCoord;

void main() {

    vec4 point = viewM * vec4(gl_in[0].gl_Position.xyz, 1.0);

    gl_Position = projectionM * (point + vec4( .5 * size.x, -.5 * size.y, 0.0, 0.0));
    texCoord = vec2(1, 0);
    EmitVertex();

    gl_Position = projectionM * (point + vec4(-.5 * size.x, -.5 * size.y, 0.0, 0.0));
    texCoord = vec2(0, 0);
    EmitVertex();

    gl_Position = projectionM * (point + vec4( .5 * size.x,  .5 * size.y, 0.0, 0.0));
    texCoord = vec2(1, 1);
    EmitVertex();

    gl_Position = projectionM * (point + vec4(-.5 * size.x,  .5 * size.y, 0.0, 0.0));
    texCoord = vec2(0, 1);
    EmitVertex();

    EndPrimitive();

}